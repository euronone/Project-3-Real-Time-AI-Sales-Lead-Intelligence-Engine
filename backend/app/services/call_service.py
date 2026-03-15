"""Call service: initiate, get, list, disposition, transcript, analysis."""

import math
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.call import Call, CallDirection, CallStatus
from app.models.call_analysis import CallAnalysis
from app.models.call_transcript import CallTranscript
from app.models.user import User
from app.schemas.analysis import AnalysisResponse
from app.schemas.call import CallInitiate, CallResponse
from app.schemas.common import PaginatedResponse
from app.services.twilio_service import TwilioService


class CallService:
    """Handles call operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def initiate_call(self, payload: CallInitiate, current_user: User) -> CallResponse:
        """Initiate an outbound call via Twilio."""
        call = Call(
            tenant_id=current_user.tenant_id,
            agent_id=current_user.id,
            lead_id=payload.lead_id,
            direction=CallDirection.OUTBOUND,
            status=CallStatus.INITIATED,
        )
        self.db.add(call)
        await self.db.flush()

        # Initiate Twilio call (stub — would call TwilioService)
        twilio_service = TwilioService(self.db)
        call_sid = await twilio_service.make_call(
            to_number=payload.phone_number or "",
            call_id=str(call.id),
        )
        call.twilio_call_sid = call_sid
        await self.db.flush()
        await self.db.refresh(call)

        return CallResponse.model_validate(call)

    async def list_calls(
        self, tenant_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> PaginatedResponse[CallResponse]:
        """List calls for a tenant with pagination."""
        query = select(Call).where(Call.tenant_id == tenant_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Call.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        calls = result.scalars().all()

        return PaginatedResponse(
            items=[CallResponse.model_validate(c) for c in calls],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )

    async def get_call(self, call_id: uuid.UUID, tenant_id: uuid.UUID) -> CallResponse:
        """Get a call by ID."""
        call = await self._get_call_or_404(call_id, tenant_id)
        return CallResponse.model_validate(call)

    async def get_transcript(self, call_id: uuid.UUID, tenant_id: uuid.UUID) -> list[dict]:
        """Get the full transcript for a call."""
        await self._get_call_or_404(call_id, tenant_id)
        result = await self.db.execute(
            select(CallTranscript)
            .where(CallTranscript.call_id == call_id)
            .order_by(CallTranscript.start_time)
        )
        transcripts = result.scalars().all()
        return [
            {
                "id": str(t.id),
                "speaker": t.speaker.value,
                "text": t.text,
                "start_time": t.start_time,
                "end_time": t.end_time,
                "confidence": t.confidence,
            }
            for t in transcripts
        ]

    async def get_analysis(self, call_id: uuid.UUID, tenant_id: uuid.UUID) -> AnalysisResponse:
        """Get AI analysis for a call."""
        await self._get_call_or_404(call_id, tenant_id)
        result = await self.db.execute(
            select(CallAnalysis).where(CallAnalysis.call_id == call_id)
        )
        analysis = result.scalar_one_or_none()
        if not analysis:
            raise NotFoundError("CallAnalysis", str(call_id))
        return AnalysisResponse.model_validate(analysis)

    async def get_recording_url(self, call_id: uuid.UUID, tenant_id: uuid.UUID) -> dict:
        """Get presigned S3 URL for a call recording."""
        call = await self._get_call_or_404(call_id, tenant_id)
        if not call.recording_url:
            raise NotFoundError("Recording", str(call_id))
        # In production, generate a presigned S3 URL
        return {"url": call.recording_url, "expires_in": 3600}

    async def set_disposition(
        self, call_id: uuid.UUID, disposition: str, tenant_id: uuid.UUID
    ) -> CallResponse:
        """Set the disposition of a call."""
        call = await self._get_call_or_404(call_id, tenant_id)
        call.disposition = disposition
        await self.db.flush()
        await self.db.refresh(call)
        return CallResponse.model_validate(call)

    async def _get_call_or_404(self, call_id: uuid.UUID, tenant_id: uuid.UUID) -> Call:
        result = await self.db.execute(
            select(Call).where(Call.id == call_id, Call.tenant_id == tenant_id)
        )
        call = result.scalar_one_or_none()
        if not call:
            raise NotFoundError("Call", str(call_id))
        return call
