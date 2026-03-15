"""Tenant schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.tenant import TenantPlan


class TenantCreate(BaseModel):
    """Schema for creating a new tenant."""

    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    plan: TenantPlan = TenantPlan.FREE


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""

    name: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, max_length=100, pattern=r"^[a-z0-9-]+$")
    plan: TenantPlan | None = None
    settings: dict | None = None
    is_active: bool | None = None


class TenantResponse(BaseModel):
    """Tenant response schema."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    slug: str
    plan: TenantPlan
    settings: dict | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
