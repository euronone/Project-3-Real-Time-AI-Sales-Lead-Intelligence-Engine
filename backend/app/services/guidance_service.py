"""Guidance service: real-time agent guidance generation."""

from app.ai.openai_client import OpenAIClient
from app.ai.prompts.guidance_prompt import build_guidance_prompt


class GuidanceService:
    """Handles real-time AI guidance for agents during calls."""

    def __init__(self) -> None:
        self.openai_client = OpenAIClient()

    async def generate_guidance(
        self,
        transcript_context: str,
        latest_utterance: str,
        call_metadata: dict | None = None,
    ) -> dict:
        """Generate real-time guidance based on the conversation.

        Args:
            transcript_context: Previous conversation transcript.
            latest_utterance: The most recent customer utterance.
            call_metadata: Optional metadata about the call/lead.

        Returns:
            Guidance dict with suggested responses, warnings, and tips.
        """
        prompt = build_guidance_prompt(
            transcript_context=transcript_context,
            latest_utterance=latest_utterance,
            metadata=call_metadata or {},
        )

        result = await self.openai_client.chat_completion(
            messages=prompt,
            response_format="json",
        )

        return {
            "suggested_responses": result.get("suggested_responses", []),
            "recommended_questions": result.get("recommended_questions", []),
            "warnings": result.get("warnings", []),
            "battle_card": result.get("battle_card"),
            "next_best_action": result.get("next_best_action"),
        }

    async def get_battle_card(
        self,
        competitor_name: str,
        product_context: str = "",
    ) -> dict:
        """Get a competitive battle card when a competitor is mentioned.

        Args:
            competitor_name: Name of the competitor mentioned.
            product_context: Context about the product being discussed.

        Returns:
            Battle card with key differentiators and talking points.
        """
        prompt = build_guidance_prompt(
            transcript_context=product_context,
            latest_utterance=f"Customer mentioned competitor: {competitor_name}",
            metadata={"type": "battle_card", "competitor": competitor_name},
        )

        result = await self.openai_client.chat_completion(
            messages=prompt,
            response_format="json",
        )

        return {
            "competitor": competitor_name,
            "differentiators": result.get("differentiators", []),
            "talking_points": result.get("talking_points", []),
            "weaknesses_to_highlight": result.get("weaknesses_to_highlight", []),
            "objection_handlers": result.get("objection_handlers", []),
        }
