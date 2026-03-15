"""Call schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.call import CallDirection, CallStatus


class CallCreate(BaseModel):
    """Schema for creating a call record."""

    agent_id: uuid.UUID
    lead_id: uuid.UUID
    direction: CallDirection = CallDirection.OUTBOUND


class CallInitiate(BaseModel):
    """Schema for initiating an outbound call."""

    lead_id: uuid.UUID
    phone_number: str | None = None


class CallDisposition(BaseModel):
    """Schema for setting call disposition."""

    disposition: str


class CallResponse(BaseModel):
    """Call response schema."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    agent_id: uuid.UUID
    lead_id: uuid.UUID
    twilio_call_sid: str | None = None
    direction: CallDirection
    status: CallStatus
    duration_seconds: int | None = None
    recording_url: str | None = None
    disposition: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    created_at: datetime
