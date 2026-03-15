"""Agent CRUD and scorecard routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[UserResponse]:
    """List all agents in the current tenant with performance metrics."""
    service = UserService(db)
    return await service.list_agents(current_user.tenant_id)


@router.get("/{agent_id}/scorecard")
async def get_agent_scorecard(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get performance scorecard for a specific agent."""
    service = UserService(db)
    return await service.get_agent_scorecard(agent_id, current_user.tenant_id)
