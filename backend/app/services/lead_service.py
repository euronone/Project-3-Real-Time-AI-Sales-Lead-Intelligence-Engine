"""Lead service with CRUD, import, assign, and related operations."""

import math
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.models.lead_flow import LeadFlow
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.lead import LeadCreate, LeadImport, LeadResponse, LeadUpdate
from app.schemas.lead_flow import LeadFlowCreate, LeadFlowResponse, LeadFlowUpdate


class LeadService:
    """Handles lead, lead flow, and campaign operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # --- Lead CRUD ---

    async def list_leads(
        self,
        tenant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        priority: str | None = None,
        assigned_agent_id: uuid.UUID | None = None,
    ) -> PaginatedResponse[LeadResponse]:
        """List leads with filtering and pagination."""
        query = select(Lead).where(Lead.tenant_id == tenant_id)

        if status:
            query = query.where(Lead.status == status)
        if priority:
            query = query.where(Lead.priority == priority)
        if assigned_agent_id:
            query = query.where(Lead.assigned_agent_id == assigned_agent_id)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Paginate
        query = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        leads = result.scalars().all()

        return PaginatedResponse(
            items=[LeadResponse.model_validate(lead) for lead in leads],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )

    async def create_lead(self, payload: LeadCreate, tenant_id: uuid.UUID) -> LeadResponse:
        """Create a new lead."""
        lead = Lead(tenant_id=tenant_id, **payload.model_dump())
        self.db.add(lead)
        await self.db.flush()
        await self.db.refresh(lead)
        return LeadResponse.model_validate(lead)

    async def import_leads(self, payload: LeadImport, tenant_id: uuid.UUID) -> MessageResponse:
        """Bulk import leads."""
        count = 0
        for lead_data in payload.leads:
            lead = Lead(tenant_id=tenant_id, **lead_data.model_dump())
            self.db.add(lead)
            count += 1
        await self.db.flush()
        return MessageResponse(message=f"Successfully imported {count} leads")

    async def get_lead(self, lead_id: uuid.UUID, tenant_id: uuid.UUID) -> LeadResponse:
        """Get lead by ID."""
        lead = await self._get_lead_or_404(lead_id, tenant_id)
        return LeadResponse.model_validate(lead)

    async def update_lead(
        self, lead_id: uuid.UUID, payload: LeadUpdate, tenant_id: uuid.UUID
    ) -> LeadResponse:
        """Update a lead."""
        lead = await self._get_lead_or_404(lead_id, tenant_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(lead, key, value)
        await self.db.flush()
        await self.db.refresh(lead)
        return LeadResponse.model_validate(lead)

    async def assign_lead(
        self, lead_id: uuid.UUID, agent_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> LeadResponse:
        """Assign a lead to an agent."""
        lead = await self._get_lead_or_404(lead_id, tenant_id)
        lead.assigned_agent_id = agent_id
        await self.db.flush()
        await self.db.refresh(lead)
        return LeadResponse.model_validate(lead)

    async def delete_lead(self, lead_id: uuid.UUID, tenant_id: uuid.UUID) -> MessageResponse:
        """Archive a lead (soft delete by changing status)."""
        lead = await self._get_lead_or_404(lead_id, tenant_id)
        await self.db.delete(lead)
        await self.db.flush()
        return MessageResponse(message="Lead archived")

    # --- Lead Flow ---

    async def list_lead_flows(self, tenant_id: uuid.UUID) -> list[LeadFlowResponse]:
        """List all lead flows for a tenant."""
        result = await self.db.execute(
            select(LeadFlow).where(LeadFlow.tenant_id == tenant_id)
        )
        flows = result.scalars().all()
        return [LeadFlowResponse.model_validate(f) for f in flows]

    async def create_lead_flow(
        self, payload: LeadFlowCreate, tenant_id: uuid.UUID
    ) -> LeadFlowResponse:
        """Create a new lead flow."""
        flow = LeadFlow(tenant_id=tenant_id, **payload.model_dump())
        self.db.add(flow)
        await self.db.flush()
        await self.db.refresh(flow)
        return LeadFlowResponse.model_validate(flow)

    async def get_lead_flow(
        self, flow_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> LeadFlowResponse:
        """Get a lead flow by ID."""
        flow = await self._get_lead_flow_or_404(flow_id, tenant_id)
        return LeadFlowResponse.model_validate(flow)

    async def update_lead_flow(
        self, flow_id: uuid.UUID, payload: LeadFlowUpdate, tenant_id: uuid.UUID
    ) -> LeadFlowResponse:
        """Update a lead flow."""
        flow = await self._get_lead_flow_or_404(flow_id, tenant_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(flow, key, value)
        await self.db.flush()
        await self.db.refresh(flow)
        return LeadFlowResponse.model_validate(flow)

    async def delete_lead_flow(
        self, flow_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> MessageResponse:
        """Delete a lead flow."""
        flow = await self._get_lead_flow_or_404(flow_id, tenant_id)
        await self.db.delete(flow)
        await self.db.flush()
        return MessageResponse(message="Lead flow deleted")

    # --- Campaign ---

    async def list_campaigns(self, tenant_id: uuid.UUID) -> list[CampaignResponse]:
        """List all campaigns for a tenant."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.tenant_id == tenant_id)
        )
        campaigns = result.scalars().all()
        return [CampaignResponse.model_validate(c) for c in campaigns]

    async def create_campaign(
        self, payload: CampaignCreate, tenant_id: uuid.UUID
    ) -> CampaignResponse:
        """Create a new campaign."""
        campaign = Campaign(tenant_id=tenant_id, **payload.model_dump())
        self.db.add(campaign)
        await self.db.flush()
        await self.db.refresh(campaign)
        return CampaignResponse.model_validate(campaign)

    async def get_campaign(
        self, campaign_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> CampaignResponse:
        """Get a campaign by ID."""
        campaign = await self._get_campaign_or_404(campaign_id, tenant_id)
        return CampaignResponse.model_validate(campaign)

    async def update_campaign(
        self, campaign_id: uuid.UUID, payload: CampaignUpdate, tenant_id: uuid.UUID
    ) -> CampaignResponse:
        """Update a campaign."""
        campaign = await self._get_campaign_or_404(campaign_id, tenant_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(campaign, key, value)
        await self.db.flush()
        await self.db.refresh(campaign)
        return CampaignResponse.model_validate(campaign)

    async def add_leads_to_campaign(
        self, campaign_id: uuid.UUID, lead_ids: list[uuid.UUID], tenant_id: uuid.UUID
    ) -> MessageResponse:
        """Add leads to a campaign."""
        await self._get_campaign_or_404(campaign_id, tenant_id)
        result = await self.db.execute(
            select(Lead).where(Lead.tenant_id == tenant_id, Lead.id.in_(lead_ids))
        )
        leads = result.scalars().all()
        for lead in leads:
            lead.campaign_id = campaign_id
        await self.db.flush()
        return MessageResponse(message=f"Added {len(leads)} leads to campaign")

    # --- Helpers ---

    async def _get_lead_or_404(self, lead_id: uuid.UUID, tenant_id: uuid.UUID) -> Lead:
        result = await self.db.execute(
            select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
        )
        lead = result.scalar_one_or_none()
        if not lead:
            raise NotFoundError("Lead", str(lead_id))
        return lead

    async def _get_lead_flow_or_404(self, flow_id: uuid.UUID, tenant_id: uuid.UUID) -> LeadFlow:
        result = await self.db.execute(
            select(LeadFlow).where(LeadFlow.id == flow_id, LeadFlow.tenant_id == tenant_id)
        )
        flow = result.scalar_one_or_none()
        if not flow:
            raise NotFoundError("LeadFlow", str(flow_id))
        return flow

    async def _get_campaign_or_404(
        self, campaign_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Campaign:
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == tenant_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise NotFoundError("Campaign", str(campaign_id))
        return campaign
