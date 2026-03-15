"""Real-time guidance prompt templates for GPT-4o."""

REALTIME_GUIDANCE_SYSTEM_PROMPT = """You are a real-time sales coaching AI for SalesIQ. During live sales calls, you provide instant guidance to help sales agents close deals.

Your guidance should be:
- Concise and actionable (agent is on a live call)
- Contextually relevant to what was just said
- Focused on moving the deal forward

Return a structured JSON response with:
- suggested_responses: Array of 1-3 short response suggestions the agent could use
- recommended_questions: Array of 1-2 questions the agent should ask next
- warnings: Array of alerts if negative signals are detected (customer frustration, going off-script, etc.)
- battle_card: Object with competitor info if a competitor was mentioned, null otherwise
- next_best_action: String describing the single most important thing the agent should do right now"""


def build_guidance_prompt(
    transcript_context: str,
    latest_utterance: str,
    metadata: dict | None = None,
) -> list[dict[str, str]]:
    """Build the real-time guidance prompt messages for GPT-4o.

    Args:
        transcript_context: Previous conversation for context.
        latest_utterance: The most recent thing said in the call.
        metadata: Optional metadata (call type, lead info, etc.).

    Returns:
        List of message dicts for the chat completion API.
    """
    meta = metadata or {}

    user_content = "Provide real-time guidance for this sales call.\n\n"

    if transcript_context:
        user_content += f"Previous conversation:\n{transcript_context}\n\n"

    user_content += f"Latest utterance:\n{latest_utterance}\n"

    if meta.get("type") == "battle_card":
        user_content += (
            f"\nCOMPETITOR MENTIONED: {meta.get('competitor', 'Unknown')}\n"
            "Please include a detailed battle card in your response with differentiators, "
            "talking points, weaknesses to highlight, and objection handlers."
        )

    return [
        {"role": "system", "content": REALTIME_GUIDANCE_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
