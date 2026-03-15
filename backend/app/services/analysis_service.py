"""Analysis service: GPT-4o call analysis."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.openai_client import OpenAIClient
from app.ai.prompts.analysis_prompt import build_analysis_prompt
from app.models.call_analysis import CallAnalysis
from app.models.call_transcript import CallTranscript


class AnalysisService:
    """Handles AI-powered call analysis."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.openai_client = OpenAIClient()

    async def analyze_call(self, call_id: uuid.UUID) -> CallAnalysis:
        """Perform deep analysis on a completed call using GPT-4o.

        Fetches the full transcript, builds an analysis prompt,
        and stores structured results.

        Args:
            call_id: The call to analyze.

        Returns:
            The created CallAnalysis record.
        """
        # Fetch transcript
        result = await self.db.execute(
            select(CallTranscript)
            .where(CallTranscript.call_id == call_id)
            .order_by(CallTranscript.start_time)
        )
        transcripts = result.scalars().all()

        transcript_text = "\n".join(
            f"[{t.speaker.value}] {t.text}" for t in transcripts
        )

        # Build prompt and call LLM
        prompt = build_analysis_prompt(transcript_text)
        llm_result = await self.openai_client.chat_completion(
            messages=prompt,
            response_format="json",
        )

        # Store analysis
        analysis = CallAnalysis(
            call_id=call_id,
            summary=llm_result.get("summary"),
            sentiment_overall=llm_result.get("sentiment_overall"),
            sentiment_timeline=llm_result.get("sentiment_timeline"),
            topics=llm_result.get("topics"),
            objections=llm_result.get("objections"),
            key_moments=llm_result.get("key_moments"),
            talk_ratio_agent=llm_result.get("talk_ratio_agent"),
            filler_word_count=llm_result.get("filler_word_count"),
            agent_score=llm_result.get("agent_score"),
            feedback=llm_result.get("feedback"),
            red_flags=llm_result.get("red_flags"),
            action_items=llm_result.get("action_items"),
        )
        self.db.add(analysis)
        await self.db.flush()
        await self.db.refresh(analysis)
        return analysis

    async def analyze_stream(
        self,
        call_id: uuid.UUID,
        transcript_chunk: str,
        context: str = "",
    ) -> dict:
        """Perform real-time streaming analysis on a transcript chunk.

        Args:
            call_id: The call being analyzed.
            transcript_chunk: The latest transcript text.
            context: Previous conversation context.

        Returns:
            Analysis results dict with sentiment, guidance, and alerts.
        """
        prompt = build_analysis_prompt(
            transcript_text=f"{context}\n{transcript_chunk}",
            streaming=True,
        )
        result = await self.openai_client.chat_completion(
            messages=prompt,
            response_format="json",
        )

        return {
            "call_id": str(call_id),
            "sentiment": result.get("sentiment_overall", 0.0),
            "guidance": result.get("guidance", []),
            "red_flags": result.get("red_flags", []),
            "topics": result.get("topics", []),
        }
