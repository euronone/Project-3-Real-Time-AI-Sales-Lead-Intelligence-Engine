"""Outbound webhook CRUD routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.services.webhook_service import WebhookService

router = APIRouter()


@router.get("")
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """List configured outbound webhooks for the current tenant."""
    service = WebhookService(db)
    return await service.list_webhooks(current_user.tenant_id)


@router.post("", status_code=201)
async def create_webhook(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Create a new outbound webhook subscription."""
    service = WebhookService(db)
    return await service.create_webhook(payload, current_user.tenant_id)


@router.patch("/{webhook_id}")
async def update_webhook(
    webhook_id: uuid.UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Update an outbound webhook."""
    service = WebhookService(db)
    return await service.update_webhook(webhook_id, payload, current_user.tenant_id)


@router.delete("/{webhook_id}", response_model=MessageResponse)
async def delete_webhook(
    webhook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Delete an outbound webhook."""
    service = WebhookService(db)
    return await service.delete_webhook(webhook_id, current_user.tenant_id)
