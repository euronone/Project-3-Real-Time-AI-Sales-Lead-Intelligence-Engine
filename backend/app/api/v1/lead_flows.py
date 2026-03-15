"""Lead flow CRUD routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.lead_flow import LeadFlowCreate, LeadFlowResponse, LeadFlowUpdate

router = APIRouter()


@router.get("", response_model=list[LeadFlowResponse])
async def list_lead_flows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LeadFlowResponse]:
    """List all lead flows for the current tenant."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.list_lead_flows(current_user.tenant_id)


@router.post("", response_model=LeadFlowResponse, status_code=201)
async def create_lead_flow(
    payload: LeadFlowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadFlowResponse:
    """Create a new lead flow."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.create_lead_flow(payload, current_user.tenant_id)


@router.get("/{flow_id}", response_model=LeadFlowResponse)
async def get_lead_flow(
    flow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadFlowResponse:
    """Get lead flow details with flow definition."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.get_lead_flow(flow_id, current_user.tenant_id)


@router.patch("/{flow_id}", response_model=LeadFlowResponse)
async def update_lead_flow(
    flow_id: uuid.UUID,
    payload: LeadFlowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadFlowResponse:
    """Update a lead flow."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.update_lead_flow(flow_id, payload, current_user.tenant_id)


@router.delete("/{flow_id}", response_model=MessageResponse)
async def delete_lead_flow(
    flow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Delete a lead flow."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.delete_lead_flow(flow_id, current_user.tenant_id)
