"""Deal prediction prompt templates for GPT-4o."""

DEAL_PREDICTION_SYSTEM_PROMPT = """You are an expert sales deal predictor for SalesIQ, an AI-powered sales intelligence platform.

Based on the provided lead information and conversation history, predict the deal outcome and return a structured JSON response with:

- win_probability: Float 0-100 representing the likelihood of closing the deal
- confidence: "low", "medium", or "high" — how confident you are in this prediction
- key_factors: Array of strings describing the main factors driving your prediction
- red_flags: Array of strings identifying risk factors that could derail the deal
- recommended_actions: Array of strings with specific next steps the agent should take
- reasoning: A paragraph explaining your prediction logic and key considerations

Base your prediction on:
1. Current deal stage and progression speed
2. Customer engagement signals
3. Objections raised and how they were handled
4. Competitive landscape indicators
5. Budget and timeline discussions
6. Decision-maker involvement"""


def build_prediction_prompt(
    lead_name: str,
    company: str,
    status: str,
    deal_value: float,
    transcript_summary: str = "",
    call_history: str = "",
) -> list[dict[str, str]]:
    """Build the prediction prompt messages for GPT-4o.

    Args:
        lead_name: Name of the lead/contact.
        company: Company name.
        status: Current deal status.
        deal_value: Estimated deal value.
        transcript_summary: Summary of recent call transcripts.
        call_history: Summary of call interaction history.

    Returns:
        List of message dicts for the chat completion API.
    """
    user_content = f"""Predict the deal outcome for this lead:

Lead: {lead_name}
Company: {company}
Current Status: {status}
Deal Value: ${deal_value:,.2f}
"""

    if transcript_summary:
        user_content += f"\nRecent Call Summary:\n{transcript_summary}\n"

    if call_history:
        user_content += f"\nCall History:\n{call_history}\n"

    return [
        {"role": "system", "content": DEAL_PREDICTION_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
