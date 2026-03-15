"""Prediction schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.deal_prediction import PredictionConfidence


class PredictionCreate(BaseModel):
    """Schema for creating a deal prediction."""

    lead_id: uuid.UUID
    call_id: uuid.UUID | None = None
    win_probability: float = Field(ge=0, le=100)
    confidence: PredictionConfidence
    key_factors: list[str] | None = None
    red_flags: list[str] | None = None
    recommended_actions: list[str] | None = None
    reasoning: str | None = None


class PredictionResponse(BaseModel):
    """Deal prediction response schema."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    lead_id: uuid.UUID
    call_id: uuid.UUID | None = None
    win_probability: float
    confidence: PredictionConfidence
    key_factors: list[str] | None = None
    red_flags: list[str] | None = None
    recommended_actions: list[str] | None = None
    reasoning: str | None = None
    created_at: datetime
