"""Campaign schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.campaign import CampaignStatus


class CampaignCreate(BaseModel):
    """Schema for creating a new campaign."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    script_template: str | None = None
    status: CampaignStatus = CampaignStatus.DRAFT
    start_date: date | None = None
    end_date: date | None = None


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    script_template: str | None = None
    status: CampaignStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class CampaignResponse(BaseModel):
    """Campaign response schema."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    script_template: str | None = None
    status: CampaignStatus
    start_date: date | None = None
    end_date: date | None = None
    created_at: datetime
    updated_at: datetime | None = None
