"""LeadFlow schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LeadFlowCreate(BaseModel):
    """Schema for creating a new lead flow."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    flow_definition: dict | None = None
    is_active: bool = True


class LeadFlowUpdate(BaseModel):
    """Schema for updating a lead flow."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    flow_definition: dict | None = None
    is_active: bool | None = None


class LeadFlowResponse(BaseModel):
    """LeadFlow response schema."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    flow_definition: dict | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
