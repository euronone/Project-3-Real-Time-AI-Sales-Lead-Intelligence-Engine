"""Notification service: send, list, mark read."""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.notification import Notification
from app.schemas.common import MessageResponse


class NotificationService:
    """Handles notification operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def send(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str = "",
        data: dict | None = None,
    ) -> Notification:
        """Create and send a notification to a user.

        Args:
            tenant_id: The tenant this notification belongs to.
            user_id: The target user.
            notification_type: Type of notification (e.g., deal_at_risk).
            title: Notification title.
            message: Notification message body.
            data: Optional contextual payload.

        Returns:
            The created Notification.
        """
        notification = Notification(
            tenant_id=tenant_id,
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data or {},
        )
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def list_notifications(self, user_id: uuid.UUID) -> list[dict]:
        """List all notifications for a user, newest first."""
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
        )
        notifications = result.scalars().all()
        return [
            {
                "id": str(n.id),
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "data": n.data,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifications
        ]

    async def mark_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> MessageResponse:
        """Mark a single notification as read."""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise NotFoundError("Notification", str(notification_id))

        notification.is_read = True
        await self.db.flush()
        return MessageResponse(message="Notification marked as read")

    async def mark_all_read(self, user_id: uuid.UUID) -> MessageResponse:
        """Mark all notifications as read for a user."""
        await self.db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .values(is_read=True)
        )
        await self.db.flush()
        return MessageResponse(message="All notifications marked as read")
