"""Webhook model."""

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin
from app.models.db_types import GUID, JSONDocument


class Webhook(Base, TenantMixin, TimestampMixin):
    """Outbound webhook subscription configuration."""

    __tablename__ = "webhooks"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    events: Mapped[list | None] = mapped_column(JSONDocument, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    tenant = relationship("Tenant")

    def __repr__(self) -> str:
        return f"<Webhook(id={self.id}, url='{self.url}')>"
