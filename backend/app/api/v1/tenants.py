"""Tenant CRUD routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.schemas.common import MessageResponse
from app.services.tenant_service import TenantService

router = APIRouter()


@router.get("", response_model=list[TenantResponse])
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TenantResponse]:
    """List all tenants (super admin only)."""
    service = TenantService(db)
    return await service.list_tenants(current_user)


@router.post("", response_model=TenantResponse, status_code=201)
async def create_tenant(
    payload: TenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TenantResponse:
    """Create a new tenant."""
    service = TenantService(db)
    return await service.create_tenant(payload, current_user)


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TenantResponse:
    """Get tenant details."""
    service = TenantService(db)
    return await service.get_tenant(tenant_id, current_user)


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: uuid.UUID,
    payload: TenantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TenantResponse:
    """Update tenant details."""
    service = TenantService(db)
    return await service.update_tenant(tenant_id, payload, current_user)


@router.delete("/{tenant_id}", response_model=MessageResponse)
async def delete_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Deactivate a tenant."""
    service = TenantService(db)
    return await service.delete_tenant(tenant_id, current_user)
