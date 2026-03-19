"""Lead model."""

import uuid
import enum
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TenantMixin, TimestampMixin
from app.models.db_types import GUID, JSONDocument


class LeadStatus(str, enum.Enum):
    """Lead lifecycle status."""

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadPriority(str, enum.Enum):
    """Lead priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Lead(Base, TenantMixin, TimestampMixin):
    """Sales lead model."""

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus), default=LeadStatus.NEW, nullable=False
    )
    priority: Mapped[LeadPriority] = mapped_column(
        Enum(LeadPriority), default=LeadPriority.MEDIUM, nullable=False
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deal_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    custom_fields: Mapped[dict | None] = mapped_column(JSONDocument, default=dict, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="leads")
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id])
    campaign = relationship("Campaign", back_populates="leads")
    calls = relationship("Call", back_populates="lead", cascade="all, delete-orphan")
    predictions = relationship("DealPrediction", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Lead(id={self.id}, name='{self.first_name} {self.last_name}')>"
