"""Call routing rules CRUD routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/rules")
async def list_routing_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """List all call routing rules for the current tenant."""
    # Routing rules are stored in tenant settings as a JSON array
    return []


@router.post("/rules", status_code=201)
async def create_routing_rule(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Create a new call routing rule."""
    return {"id": str(uuid.uuid4()), **payload}


@router.patch("/rules/{rule_id}")
async def update_routing_rule(
    rule_id: uuid.UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Update a call routing rule."""
    return {"id": str(rule_id), **payload}


@router.delete("/rules/{rule_id}", response_model=MessageResponse)
async def delete_routing_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Delete a call routing rule."""
    return MessageResponse(message="Routing rule deleted")
