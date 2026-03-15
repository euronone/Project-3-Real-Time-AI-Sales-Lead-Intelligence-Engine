"""Lead CRUD, import, and assignment routes."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.lead import LeadAssign, LeadCreate, LeadImport, LeadResponse, LeadUpdate
from app.services.lead_service import LeadService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[LeadResponse])
async def list_leads(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = None,
    priority: str | None = None,
    assigned_agent_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[LeadResponse]:
    """List leads with filtering and pagination."""
    service = LeadService(db)
    return await service.list_leads(
        tenant_id=current_user.tenant_id,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        assigned_agent_id=assigned_agent_id,
    )


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    """Create a new lead."""
    service = LeadService(db)
    return await service.create_lead(payload, current_user.tenant_id)


@router.post("/import", response_model=MessageResponse, status_code=201)
async def import_leads(
    payload: LeadImport,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Bulk import leads."""
    service = LeadService(db)
    return await service.import_leads(payload, current_user.tenant_id)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    """Get lead details with full history."""
    service = LeadService(db)
    return await service.get_lead(lead_id, current_user.tenant_id)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: uuid.UUID,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    """Update a lead."""
    service = LeadService(db)
    return await service.update_lead(lead_id, payload, current_user.tenant_id)


@router.post("/{lead_id}/assign", response_model=LeadResponse)
async def assign_lead(
    lead_id: uuid.UUID,
    payload: LeadAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    """Assign a lead to an agent."""
    service = LeadService(db)
    return await service.assign_lead(lead_id, payload.agent_id, current_user.tenant_id)


@router.delete("/{lead_id}", response_model=MessageResponse)
async def delete_lead(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Archive a lead."""
    service = LeadService(db)
    return await service.delete_lead(lead_id, current_user.tenant_id)
