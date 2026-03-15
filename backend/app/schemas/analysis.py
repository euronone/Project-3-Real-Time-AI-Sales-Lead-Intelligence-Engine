"""Analysis schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class SentimentData(BaseModel):
    """A single sentiment data point."""

    time: float
    score: float


class RedFlag(BaseModel):
    """A detected red flag in a call."""

    type: str
    description: str
    timestamp: float | None = None
    severity: str = "medium"


class AnalysisResponse(BaseModel):
    """Call analysis response schema."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    call_id: uuid.UUID
    summary: str | None = None
    sentiment_overall: float | None = None
    sentiment_timeline: list[SentimentData] | None = None
    topics: list[str] | None = None
    objections: list[str] | None = None
    key_moments: list[dict] | None = None
    talk_ratio_agent: float | None = None
    filler_word_count: int | None = None
    agent_score: float | None = None
    feedback: str | None = None
    red_flags: list[RedFlag] | None = None
    action_items: list[str] | None = None
    created_at: datetime
