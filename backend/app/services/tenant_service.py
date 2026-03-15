"""Tenant service with CRUD operations."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate


class TenantService:
    """Handles tenant CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_tenants(self, current_user: User) -> list[TenantResponse]:
        """List all tenants (super admin) or the current user's tenant."""
        if current_user.role == UserRole.SUPER_ADMIN:
            result = await self.db.execute(select(Tenant))
            tenants = result.scalars().all()
        else:
            result = await self.db.execute(
                select(Tenant).where(Tenant.id == current_user.tenant_id)
            )
            tenants = result.scalars().all()
        return [TenantResponse.model_validate(t) for t in tenants]

    async def create_tenant(self, payload: TenantCreate, current_user: User) -> TenantResponse:
        """Create a new tenant (super admin only)."""
        if current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenError("Only super admins can create tenants")

        tenant = Tenant(**payload.model_dump())
        self.db.add(tenant)
        await self.db.flush()
        await self.db.refresh(tenant)
        return TenantResponse.model_validate(tenant)

    async def get_tenant(self, tenant_id: uuid.UUID, current_user: User) -> TenantResponse:
        """Get tenant by ID."""
        tenant = await self._get_tenant_or_404(tenant_id)
        if current_user.role != UserRole.SUPER_ADMIN and current_user.tenant_id != tenant_id:
            raise ForbiddenError()
        return TenantResponse.model_validate(tenant)

    async def update_tenant(
        self, tenant_id: uuid.UUID, payload: TenantUpdate, current_user: User
    ) -> TenantResponse:
        """Update tenant details."""
        tenant = await self._get_tenant_or_404(tenant_id)
        if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN):
            raise ForbiddenError()
        if current_user.role == UserRole.TENANT_ADMIN and current_user.tenant_id != tenant_id:
            raise ForbiddenError()

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tenant, key, value)
        await self.db.flush()
        await self.db.refresh(tenant)
        return TenantResponse.model_validate(tenant)

    async def delete_tenant(self, tenant_id: uuid.UUID, current_user: User) -> MessageResponse:
        """Deactivate a tenant."""
        if current_user.role != UserRole.SUPER_ADMIN:
            raise ForbiddenError("Only super admins can deactivate tenants")
        tenant = await self._get_tenant_or_404(tenant_id)
        tenant.is_active = False
        await self.db.flush()
        return MessageResponse(message="Tenant deactivated")

    async def _get_tenant_or_404(self, tenant_id: uuid.UUID) -> Tenant:
        """Fetch a tenant or raise NotFoundError."""
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise NotFoundError("Tenant", str(tenant_id))
        return tenant
