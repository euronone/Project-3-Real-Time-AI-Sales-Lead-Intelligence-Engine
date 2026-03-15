"""Notification routes: list, mark read, mark all read."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("")
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """List notifications for the current user."""
    service = NotificationService(db)
    return await service.list_notifications(current_user.id)


@router.patch("/{notification_id}/read", response_model=MessageResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Mark a notification as read."""
    service = NotificationService(db)
    return await service.mark_read(notification_id, current_user.id)


@router.patch("/read-all", response_model=MessageResponse)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Mark all notifications as read."""
    service = NotificationService(db)
    return await service.mark_all_read(current_user.id)
