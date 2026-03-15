"""Lead schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.models.lead import LeadPriority, LeadStatus


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company: str | None = Field(default=None, max_length=255)
    title: str | None = Field(default=None, max_length=255)
    status: LeadStatus = LeadStatus.NEW
    priority: LeadPriority = LeadPriority.MEDIUM
    source: str | None = Field(default=None, max_length=100)
    deal_value: Decimal | None = None
    campaign_id: uuid.UUID | None = None
    custom_fields: dict | None = None


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company: str | None = Field(default=None, max_length=255)
    title: str | None = Field(default=None, max_length=255)
    status: LeadStatus | None = None
    priority: LeadPriority | None = None
    source: str | None = Field(default=None, max_length=100)
    deal_value: Decimal | None = None
    campaign_id: uuid.UUID | None = None
    custom_fields: dict | None = None


class LeadResponse(BaseModel):
    """Lead response schema."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    assigned_agent_id: uuid.UUID | None = None
    campaign_id: uuid.UUID | None = None
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    title: str | None = None
    status: LeadStatus
    priority: LeadPriority
    source: str | None = None
    deal_value: Decimal | None = None
    custom_fields: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None


class LeadImport(BaseModel):
    """Schema for bulk lead import."""

    leads: list[LeadCreate]


class LeadAssign(BaseModel):
    """Schema for assigning a lead to an agent."""

    agent_id: uuid.UUID
