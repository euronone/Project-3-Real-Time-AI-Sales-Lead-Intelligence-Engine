"""Call analysis prompt templates for GPT-4o."""

CALL_ANALYSIS_SYSTEM_PROMPT = """You are an expert sales call analyst for SalesIQ, an AI-powered sales intelligence platform.

Analyze the provided sales call transcript and return a structured JSON response with the following fields:

- summary: A concise 2-3 sentence summary of the call
- sentiment_overall: Float between -1.0 (very negative) and 1.0 (very positive)
- sentiment_timeline: Array of {time: float, score: float} tracking sentiment changes
- topics: Array of key topics discussed
- objections: Array of customer objections detected
- key_moments: Array of {time: float, type: string, description: string} for important moments
- talk_ratio_agent: Float 0-1 representing what percentage of the call the agent spoke
- filler_word_count: Integer count of filler words (um, uh, like, you know, etc.)
- agent_score: Float 0-100 overall agent performance score
- feedback: Specific coaching feedback for the agent
- red_flags: Array of {type: string, description: string, severity: string} for concerning moments
- action_items: Array of follow-up actions extracted from the conversation

Be specific and actionable in your feedback. Base all analysis on the actual transcript content."""


def build_analysis_prompt(
    transcript_text: str,
    streaming: bool = False,
) -> list[dict[str, str]]:
    """Build the analysis prompt messages for GPT-4o.

    Args:
        transcript_text: The call transcript text to analyze.
        streaming: If True, generate a lighter analysis for real-time use.

    Returns:
        List of message dicts for the chat completion API.
    """
    if streaming:
        system_content = (
            "You are a real-time sales call analyst. Analyze the latest portion of the "
            "conversation and return JSON with: sentiment_overall (float), guidance (array of "
            "suggested talking points), red_flags (array of alerts), topics (array of detected topics)."
        )
    else:
        system_content = CALL_ANALYSIS_SYSTEM_PROMPT

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"Analyze this sales call transcript:\n\n{transcript_text}"},
    ]
