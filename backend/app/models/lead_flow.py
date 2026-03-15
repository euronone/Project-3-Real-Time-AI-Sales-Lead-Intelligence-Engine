"""LeadFlow model."""

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin


class LeadFlow(Base, TenantMixin, TimestampMixin):
    """Lead flow definition for call sequences and follow-up cadences."""

    __tablename__ = "lead_flows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    flow_definition: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="lead_flows")

    def __repr__(self) -> str:
        return f"<LeadFlow(id={self.id}, name='{self.name}')>"
