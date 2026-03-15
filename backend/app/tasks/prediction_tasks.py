"""Celery tasks for deal prediction recalculation."""

import asyncio
import uuid

import structlog

from app.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.prediction_tasks.recalculate_prediction", bind=True)
def recalculate_prediction(self, call_id: str) -> dict:
    """Recalculate deal prediction after a call is analyzed.

    Args:
        call_id: The call UUID string that triggered recalculation.

    Returns:
        Dict with prediction task result.
    """
    logger.info("recalculate_prediction_started", call_id=call_id)

    async def _run() -> dict:
        from sqlalchemy import select

        from app.core.database import async_session_factory
        from app.models.call import Call
        from app.models.lead import Lead
        from app.services.prediction_service import PredictionService

        async with async_session_factory() as db:
            # Get call and lead
            result = await db.execute(
                select(Call).where(Call.id == uuid.UUID(call_id))
            )
            call = result.scalar_one_or_none()

            if not call:
                return {"call_id": call_id, "status": "call_not_found"}

            result = await db.execute(
                select(Lead).where(Lead.id == call.lead_id)
            )
            lead = result.scalar_one_or_none()

            if not lead:
                return {"call_id": call_id, "status": "lead_not_found"}

            service = PredictionService(db)
            prediction = await service.predict_deal(lead, call_id=call.id)
            await db.commit()

            return {
                "call_id": call_id,
                "prediction_id": str(prediction.id),
                "win_probability": prediction.win_probability,
                "status": "completed",
            }

    result = asyncio.get_event_loop().run_until_complete(_run())
    logger.info("recalculate_prediction_completed", call_id=call_id)
    return result
