"""Campaign CRUD routes."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("", response_model=list[CampaignResponse])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CampaignResponse]:
    """List all campaigns for the current tenant."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.list_campaigns(current_user.tenant_id)


@router.post("", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    payload: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CampaignResponse:
    """Create a new campaign."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.create_campaign(payload, current_user.tenant_id)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CampaignResponse:
    """Get campaign detail with metrics."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.get_campaign(campaign_id, current_user.tenant_id)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID,
    payload: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CampaignResponse:
    """Update a campaign."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.update_campaign(campaign_id, payload, current_user.tenant_id)


@router.post("/{campaign_id}/leads", response_model=MessageResponse)
async def add_leads_to_campaign(
    campaign_id: uuid.UUID,
    lead_ids: list[uuid.UUID],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Add leads to a campaign."""
    from app.services.lead_service import LeadService

    service = LeadService(db)
    return await service.add_leads_to_campaign(campaign_id, lead_ids, current_user.tenant_id)
