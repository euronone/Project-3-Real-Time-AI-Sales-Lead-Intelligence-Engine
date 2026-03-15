"""Webhook service: outbound webhook CRUD and dispatch."""

import uuid

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.webhook import Webhook
from app.schemas.common import MessageResponse

logger = structlog.get_logger(__name__)


class WebhookService:
    """Handles outbound webhook operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_webhooks(self, tenant_id: uuid.UUID) -> list[dict]:
        """List all webhooks for a tenant."""
        result = await self.db.execute(
            select(Webhook).where(Webhook.tenant_id == tenant_id)
        )
        webhooks = result.scalars().all()
        return [
            {
                "id": str(w.id),
                "url": w.url,
                "events": w.events,
                "is_active": w.is_active,
                "description": w.description,
                "created_at": w.created_at.isoformat() if w.created_at else None,
            }
            for w in webhooks
        ]

    async def create_webhook(self, payload: dict, tenant_id: uuid.UUID) -> dict:
        """Create a new outbound webhook subscription."""
        webhook = Webhook(
            tenant_id=tenant_id,
            url=payload.get("url", ""),
            secret=payload.get("secret"),
            events=payload.get("events", []),
            is_active=payload.get("is_active", True),
            description=payload.get("description"),
        )
        self.db.add(webhook)
        await self.db.flush()
        await self.db.refresh(webhook)
        return {
            "id": str(webhook.id),
            "url": webhook.url,
            "events": webhook.events,
            "is_active": webhook.is_active,
            "description": webhook.description,
        }

    async def update_webhook(
        self, webhook_id: uuid.UUID, payload: dict, tenant_id: uuid.UUID
    ) -> dict:
        """Update an outbound webhook."""
        webhook = await self._get_webhook_or_404(webhook_id, tenant_id)
        for key, value in payload.items():
            if hasattr(webhook, key):
                setattr(webhook, key, value)
        await self.db.flush()
        await self.db.refresh(webhook)
        return {
            "id": str(webhook.id),
            "url": webhook.url,
            "events": webhook.events,
            "is_active": webhook.is_active,
            "description": webhook.description,
        }

    async def delete_webhook(
        self, webhook_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> MessageResponse:
        """Delete an outbound webhook."""
        webhook = await self._get_webhook_or_404(webhook_id, tenant_id)
        await self.db.delete(webhook)
        await self.db.flush()
        return MessageResponse(message="Webhook deleted")

    async def dispatch(
        self,
        tenant_id: uuid.UUID,
        event_type: str,
        payload: dict,
    ) -> None:
        """Dispatch an event to all matching active webhooks for a tenant.

        Args:
            tenant_id: The tenant whose webhooks to dispatch to.
            event_type: The event type (e.g., call.completed).
            payload: The event payload data.
        """
        result = await self.db.execute(
            select(Webhook).where(
                Webhook.tenant_id == tenant_id,
                Webhook.is_active == True,  # noqa: E712
            )
        )
        webhooks = result.scalars().all()

        async with httpx.AsyncClient(timeout=10.0) as client:
            for webhook in webhooks:
                if webhook.events and event_type not in webhook.events:
                    continue
                try:
                    await client.post(
                        webhook.url,
                        json={"event": event_type, "data": payload},
                        headers={"X-Webhook-Secret": webhook.secret or ""},
                    )
                except Exception as e:
                    logger.error(
                        "webhook_dispatch_failed",
                        webhook_id=str(webhook.id),
                        error=str(e),
                    )

    async def _get_webhook_or_404(
        self, webhook_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Webhook:
        result = await self.db.execute(
            select(Webhook).where(
                Webhook.id == webhook_id,
                Webhook.tenant_id == tenant_id,
            )
        )
        webhook = result.scalar_one_or_none()
        if not webhook:
            raise NotFoundError("Webhook", str(webhook_id))
        return webhook
