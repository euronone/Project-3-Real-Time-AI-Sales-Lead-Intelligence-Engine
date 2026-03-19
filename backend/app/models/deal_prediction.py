"""DealPrediction model."""

import uuid
import enum

from sqlalchemy import Enum, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.db_types import GUID, JSONDocument


class PredictionConfidence(str, enum.Enum):
    """Confidence level for a deal prediction."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DealPrediction(Base, TimestampMixin):
    """AI-generated deal outcome prediction."""

    __tablename__ = "deal_predictions"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    call_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID, ForeignKey("calls.id", ondelete="SET NULL"), nullable=True
    )
    win_probability: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[PredictionConfidence] = mapped_column(
        Enum(PredictionConfidence), nullable=False
    )
    key_factors: Mapped[list | None] = mapped_column(JSONDocument, nullable=True)
    red_flags: Mapped[list | None] = mapped_column(JSONDocument, nullable=True)
    recommended_actions: Mapped[list | None] = mapped_column(JSONDocument, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    lead = relationship("Lead", back_populates="predictions")
    call = relationship("Call")

    def __repr__(self) -> str:
        return f"<DealPrediction(id={self.id}, win_probability={self.win_probability})>"
