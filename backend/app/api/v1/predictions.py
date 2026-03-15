"""Deal prediction endpoints: pipeline, lead predictions, refresh."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.prediction import PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.get("/pipeline")
async def get_prediction_pipeline(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get all deals with AI predictions for pipeline view."""
    service = PredictionService(db)
    return await service.get_pipeline(current_user.tenant_id)


@router.get("/lead/{lead_id}", response_model=list[PredictionResponse])
async def get_lead_predictions(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PredictionResponse]:
    """Get prediction history for a specific lead."""
    service = PredictionService(db)
    return await service.get_lead_predictions(lead_id, current_user.tenant_id)


@router.post("/lead/{lead_id}/refresh", response_model=PredictionResponse)
async def refresh_lead_prediction(
    lead_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PredictionResponse:
    """Force re-prediction for a lead."""
    service = PredictionService(db)
    return await service.refresh_prediction(lead_id, current_user.tenant_id)
