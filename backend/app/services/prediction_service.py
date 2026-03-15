"""Prediction service: AI deal outcome prediction."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.openai_client import OpenAIClient
from app.ai.prompts.prediction_prompt import build_prediction_prompt
from app.core.exceptions import NotFoundError
from app.models.deal_prediction import DealPrediction, PredictionConfidence
from app.models.lead import Lead
from app.schemas.prediction import PredictionResponse


class PredictionService:
    """Handles AI-powered deal predictions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.openai_client = OpenAIClient()

    async def get_pipeline(self, tenant_id: uuid.UUID) -> list[dict]:
        """Get all deals with their latest AI predictions for pipeline view."""
        result = await self.db.execute(
            select(Lead).where(Lead.tenant_id == tenant_id).order_by(Lead.created_at.desc())
        )
        leads = result.scalars().all()

        pipeline = []
        for lead in leads:
            # Get latest prediction
            pred_result = await self.db.execute(
                select(DealPrediction)
                .where(DealPrediction.lead_id == lead.id)
                .order_by(DealPrediction.created_at.desc())
                .limit(1)
            )
            prediction = pred_result.scalar_one_or_none()

            pipeline.append({
                "lead_id": str(lead.id),
                "lead_name": f"{lead.first_name} {lead.last_name}",
                "company": lead.company,
                "status": lead.status.value,
                "deal_value": float(lead.deal_value) if lead.deal_value else None,
                "win_probability": prediction.win_probability if prediction else None,
                "confidence": prediction.confidence.value if prediction else None,
            })

        return pipeline

    async def get_lead_predictions(
        self, lead_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[PredictionResponse]:
        """Get prediction history for a specific lead."""
        # Verify lead belongs to tenant
        result = await self.db.execute(
            select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundError("Lead", str(lead_id))

        result = await self.db.execute(
            select(DealPrediction)
            .where(DealPrediction.lead_id == lead_id)
            .order_by(DealPrediction.created_at.desc())
        )
        predictions = result.scalars().all()
        return [PredictionResponse.model_validate(p) for p in predictions]

    async def refresh_prediction(
        self, lead_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> PredictionResponse:
        """Force a re-prediction for a lead using GPT-4o."""
        result = await self.db.execute(
            select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
        )
        lead = result.scalar_one_or_none()
        if not lead:
            raise NotFoundError("Lead", str(lead_id))

        return await self.predict_deal(lead)

    async def predict_deal(
        self, lead: Lead, call_id: uuid.UUID | None = None
    ) -> PredictionResponse:
        """Generate a deal prediction using GPT-4o.

        Args:
            lead: The lead to predict.
            call_id: Optional call that triggered this prediction.

        Returns:
            The created prediction response.
        """
        prompt = build_prediction_prompt(
            lead_name=f"{lead.first_name} {lead.last_name}",
            company=lead.company or "Unknown",
            status=lead.status.value,
            deal_value=float(lead.deal_value) if lead.deal_value else 0,
        )

        llm_result = await self.openai_client.chat_completion(
            messages=prompt,
            response_format="json",
        )

        confidence_map = {"low": PredictionConfidence.LOW, "medium": PredictionConfidence.MEDIUM, "high": PredictionConfidence.HIGH}

        prediction = DealPrediction(
            lead_id=lead.id,
            call_id=call_id,
            win_probability=llm_result.get("win_probability", 50.0),
            confidence=confidence_map.get(llm_result.get("confidence", "medium"), PredictionConfidence.MEDIUM),
            key_factors=llm_result.get("key_factors", []),
            red_flags=llm_result.get("red_flags", []),
            recommended_actions=llm_result.get("recommended_actions", []),
            reasoning=llm_result.get("reasoning", ""),
        )
        self.db.add(prediction)
        await self.db.flush()
        await self.db.refresh(prediction)
        return PredictionResponse.model_validate(prediction)
