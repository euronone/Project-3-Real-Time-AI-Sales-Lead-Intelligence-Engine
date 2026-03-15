"""Transcription service: OpenAI Whisper integration."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.openai_client import OpenAIClient
from app.models.call_transcript import CallTranscript, Speaker


class TranscriptionService:
    """Handles audio transcription via OpenAI Whisper."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.openai_client = OpenAIClient()

    async def transcribe_audio(
        self,
        call_id: uuid.UUID,
        audio_data: bytes,
        speaker: Speaker = Speaker.AGENT,
    ) -> CallTranscript:
        """Transcribe an audio file and store the transcript segment.

        Args:
            call_id: The call this transcript belongs to.
            audio_data: Raw audio bytes (WAV format).
            speaker: Who is speaking in this segment.

        Returns:
            The created CallTranscript record.
        """
        result = await self.openai_client.whisper_transcribe(audio_data)

        transcript = CallTranscript(
            call_id=call_id,
            speaker=speaker,
            text=result.get("text", ""),
            start_time=result.get("start_time", 0.0),
            end_time=result.get("end_time", 0.0),
            confidence=result.get("confidence"),
        )
        self.db.add(transcript)
        await self.db.flush()
        await self.db.refresh(transcript)
        return transcript

    async def transcribe_stream(
        self,
        call_id: uuid.UUID,
        audio_chunk: bytes,
        chunk_index: int,
        speaker: Speaker = Speaker.AGENT,
    ) -> CallTranscript | None:
        """Transcribe a streaming audio chunk.

        For real-time transcription, audio chunks are accumulated and
        transcribed when enough data is available.

        Args:
            call_id: The call this transcript belongs to.
            audio_chunk: Raw audio chunk bytes.
            chunk_index: The index of this chunk in the stream.
            speaker: Who is speaking.

        Returns:
            A CallTranscript if transcription was performed, None otherwise.
        """
        result = await self.openai_client.whisper_transcribe(audio_chunk)

        if not result.get("text"):
            return None

        transcript = CallTranscript(
            call_id=call_id,
            speaker=speaker,
            text=result["text"],
            start_time=chunk_index * 0.5,
            end_time=(chunk_index + 1) * 0.5,
            confidence=result.get("confidence"),
        )
        self.db.add(transcript)
        await self.db.flush()
        await self.db.refresh(transcript)
        return transcript
