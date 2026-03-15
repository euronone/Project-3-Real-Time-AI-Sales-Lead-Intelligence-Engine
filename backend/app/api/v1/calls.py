"""Call records, transcripts, analysis, recording, initiate, and disposition routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.analysis import AnalysisResponse
from app.schemas.call import CallDisposition, CallInitiate, CallResponse
from app.schemas.common import PaginatedResponse
from app.services.call_service import CallService

router = APIRouter()


@router.post("/initiate", response_model=CallResponse, status_code=201)
async def initiate_call(
    payload: CallInitiate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallResponse:
    """Initiate an outbound call."""
    service = CallService(db)
    return await service.initiate_call(payload, current_user)


@router.get("", response_model=PaginatedResponse[CallResponse])
async def list_calls(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[CallResponse]:
    """List call records for the current tenant."""
    service = CallService(db)
    return await service.list_calls(current_user.tenant_id, page, page_size)


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallResponse:
    """Get call detail with transcript and analysis."""
    service = CallService(db)
    return await service.get_call(call_id, current_user.tenant_id)


@router.get("/{call_id}/transcript")
async def get_call_transcript(
    call_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get the full transcript for a call."""
    service = CallService(db)
    return await service.get_transcript(call_id, current_user.tenant_id)


@router.get("/{call_id}/analysis", response_model=AnalysisResponse)
async def get_call_analysis(
    call_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisResponse:
    """Get AI analysis results for a call."""
    service = CallService(db)
    return await service.get_analysis(call_id, current_user.tenant_id)


@router.get("/{call_id}/recording")
async def get_call_recording(
    call_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get presigned S3 URL for call recording playback."""
    service = CallService(db)
    return await service.get_recording_url(call_id, current_user.tenant_id)


@router.post("/{call_id}/disposition", response_model=CallResponse)
async def set_call_disposition(
    call_id: uuid.UUID,
    payload: CallDisposition,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallResponse:
    """Set call disposition."""
    service = CallService(db)
    return await service.set_disposition(call_id, payload.disposition, current_user.tenant_id)
