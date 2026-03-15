"""Celery tasks for post-call deep analysis."""

import asyncio
import uuid

import structlog

from app.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.analysis_tasks.analyze_call_recording", bind=True)
def analyze_call_recording(self, call_id: str) -> dict:
    """Run deep AI analysis on a completed call.

    Args:
        call_id: The call UUID string.

    Returns:
        Dict with analysis task result.
    """
    logger.info("analyze_call_started", call_id=call_id)

    async def _run() -> dict:
        from app.core.database import async_session_factory
        from app.services.analysis_service import AnalysisService

        async with async_session_factory() as db:
            service = AnalysisService(db)
            analysis = await service.analyze_call(uuid.UUID(call_id))
            await db.commit()

            return {
                "call_id": call_id,
                "analysis_id": str(analysis.id),
                "status": "completed",
            }

    result = asyncio.get_event_loop().run_until_complete(_run())

    # Trigger prediction recalculation
    from app.tasks.prediction_tasks import recalculate_prediction
    recalculate_prediction.delay(call_id)

    logger.info("analyze_call_completed", call_id=call_id)
    return result
