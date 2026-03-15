"""CallAnalysis model."""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CallAnalysis(Base, TimestampMixin):
    """AI-generated analysis for a call (one-to-one with Call)."""

    __tablename__ = "call_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    call_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("calls.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment_overall: Mapped[float | None] = mapped_column(Float, nullable=True)
    sentiment_timeline: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    topics: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    objections: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    key_moments: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    talk_ratio_agent: Mapped[float | None] = mapped_column(Float, nullable=True)
    filler_word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    agent_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    red_flags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    action_items: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    call = relationship("Call", back_populates="analysis")

    def __repr__(self) -> str:
        return f"<CallAnalysis(id={self.id}, call_id={self.call_id})>"
