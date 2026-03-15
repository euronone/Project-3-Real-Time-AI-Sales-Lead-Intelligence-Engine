"""AI Pipeline: orchestrates STT -> analysis -> prediction."""

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_transcript import Speaker
from app.services.analysis_service import AnalysisService
from app.services.guidance_service import GuidanceService
from app.services.prediction_service import PredictionService
from app.services.transcription_service import TranscriptionService

logger = structlog.get_logger(__name__)


class AIPipeline:
    """Orchestrates the full AI pipeline from audio to insights.

    Pipeline stages:
    1. Speech-to-Text (Whisper)
    2. Real-time analysis (GPT-4o)
    3. Guidance generation
    4. Deal prediction (post-call)
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.transcription_service = TranscriptionService(db)
        self.analysis_service = AnalysisService(db)
        self.guidance_service = GuidanceService()
        self.prediction_service = PredictionService(db)

    async def process_audio_chunk(
        self,
        call_id: uuid.UUID,
        audio_chunk: bytes,
        chunk_index: int,
        transcript_context: str = "",
    ) -> dict:
        """Process a single audio chunk through the real-time pipeline.

        Args:
            call_id: The active call ID.
            audio_chunk: Raw audio bytes to transcribe.
            chunk_index: Index of this chunk in the stream.
            transcript_context: Previous transcript for context.

        Returns:
            Dict with transcript, analysis, and guidance results.
        """
        result: dict = {
            "transcript": None,
            "analysis": None,
            "guidance": None,
        }

        # Step 1: Transcribe audio chunk
        transcript = await self.transcription_service.transcribe_stream(
            call_id=call_id,
            audio_chunk=audio_chunk,
            chunk_index=chunk_index,
            speaker=Speaker.CUSTOMER,
        )

        if not transcript:
            return result

        result["transcript"] = {
            "text": transcript.text,
            "speaker": transcript.speaker.value,
            "start_time": transcript.start_time,
            "end_time": transcript.end_time,
        }

        # Step 2: Real-time analysis
        analysis = await self.analysis_service.analyze_stream(
            call_id=call_id,
            transcript_chunk=transcript.text,
            context=transcript_context,
        )
        result["analysis"] = analysis

        # Step 3: Generate guidance
        guidance = await self.guidance_service.generate_guidance(
            transcript_context=transcript_context,
            latest_utterance=transcript.text,
        )
        result["guidance"] = guidance

        logger.info(
            "pipeline_chunk_processed",
            call_id=str(call_id),
            chunk_index=chunk_index,
        )

        return result

    async def process_completed_call(
        self,
        call_id: uuid.UUID,
        lead_id: uuid.UUID,
    ) -> dict:
        """Run the full post-call analysis pipeline.

        Args:
            call_id: The completed call ID.
            lead_id: The lead associated with the call.

        Returns:
            Dict with analysis and prediction results.
        """
        # Step 1: Deep analysis
        analysis = await self.analysis_service.analyze_call(call_id)

        # Step 2: Deal prediction
        from sqlalchemy import select
        from app.models.lead import Lead

        result = await self.db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()

        prediction = None
        if lead:
            prediction = await self.prediction_service.predict_deal(lead, call_id=call_id)

        logger.info(
            "pipeline_post_call_completed",
            call_id=str(call_id),
            lead_id=str(lead_id),
        )

        return {
            "analysis_id": str(analysis.id),
            "prediction_id": str(prediction.id) if prediction else None,
        }
