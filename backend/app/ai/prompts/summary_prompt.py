"""Post-call summary prompt templates for GPT-4o."""

CALL_SUMMARY_SYSTEM_PROMPT = """You are a sales call summarizer for SalesIQ, an AI-powered sales intelligence platform.

Given a complete call transcript, generate a comprehensive post-call summary in JSON format with:

- executive_summary: 2-3 sentence overview of the call
- key_topics: Array of main topics discussed
- customer_needs: Array of identified customer needs/pain points
- commitments_made: Array of commitments or promises made by either party
- action_items: Array of {owner: "agent"|"customer", item: string, deadline: string|null}
- next_steps: String describing agreed-upon next steps
- deal_stage_recommendation: Suggested deal stage based on the conversation
- follow_up_date: Recommended follow-up date (ISO format or null)

Focus on extracting actionable information that helps the agent prepare for the next interaction."""


def build_summary_prompt(
    transcript_text: str,
    lead_context: str = "",
) -> list[dict[str, str]]:
    """Build the post-call summary prompt messages for GPT-4o.

    Args:
        transcript_text: The full call transcript.
        lead_context: Optional context about the lead and deal history.

    Returns:
        List of message dicts for the chat completion API.
    """
    user_content = f"Summarize this completed sales call:\n\n{transcript_text}"

    if lead_context:
        user_content += f"\n\nLead Context:\n{lead_context}"

    return [
        {"role": "system", "content": CALL_SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
