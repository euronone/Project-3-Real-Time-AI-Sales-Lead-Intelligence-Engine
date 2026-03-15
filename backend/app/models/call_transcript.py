"""CallTranscript model."""

import uuid
import enum
from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Speaker(str, enum.Enum):
    """Speaker in a call transcript segment."""

    AGENT = "agent"
    CUSTOMER = "customer"


class CallTranscript(Base, TimestampMixin):
    """Individual transcript segment from a call."""

    __tablename__ = "call_transcripts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    call_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("calls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    speaker: Mapped[Speaker] = mapped_column(Enum(Speaker), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    call = relationship("Call", back_populates="transcripts")

    def __repr__(self) -> str:
        return f"<CallTranscript(id={self.id}, speaker={self.speaker})>"
