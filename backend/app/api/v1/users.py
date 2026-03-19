"""User management routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_role
from app.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

_admin_guard = require_role(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN, UserRole.MANAGER)
_write_guard = require_role(UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN)


@router.get("", response_model=list[UserResponse], dependencies=[Depends(_admin_guard)])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserResponse]:
    """List all users in the current tenant."""
    service = UserService(db)
    return await service.list_users(current_user.tenant_id)


@router.post("", response_model=UserResponse, status_code=201, dependencies=[Depends(_write_guard)])
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Create a new user / invite agent within the current tenant."""
    service = UserService(db)
    return await service.create_user(payload, current_user.tenant_id)


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(_admin_guard)])
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get user details."""
    service = UserService(db)
    return await service.get_user(user_id, current_user.tenant_id)


@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(_write_guard)])
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update user details."""
    service = UserService(db)
    return await service.update_user(user_id, payload, current_user.tenant_id)


@router.delete("/{user_id}", response_model=MessageResponse, dependencies=[Depends(_write_guard)])
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Deactivate a user."""
    service = UserService(db)
    return await service.delete_user(user_id, current_user.tenant_id)
