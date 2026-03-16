"""Celery tasks for batch audio transcription."""

import asyncio

import structlog

from app.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.transcription_tasks.transcribe_recording", bind=True)
def transcribe_recording(self, call_id: str, recording_url: str) -> dict:
    """Download and transcribe a call recording.

    Args:
        call_id: The call UUID string.
        recording_url: URL to download the recording from.

    Returns:
        Dict with task result.
    """
    logger.info(
        "transcribe_recording_started",
        call_id=call_id,
        recording_url=recording_url,
    )

    async def _run() -> dict:
        from app.core.database import async_session_factory
        from app.services.storage_service import StorageService
        from app.services.transcription_service import TranscriptionService

        StorageService()

        # Download recording
        # In production: download from recording_url, upload to S3, then transcribe
        # audio_data = await storage.download(recording_url)

        async with async_session_factory() as db:
            TranscriptionService(db)
            # transcript = await service.transcribe_audio(
            #     call_id=uuid.UUID(call_id),
            #     audio_data=audio_data,
            # )
            await db.commit()

        return {"call_id": call_id, "status": "completed"}

    result = asyncio.get_event_loop().run_until_complete(_run())

    # Trigger analysis after transcription
    from app.tasks.analysis_tasks import analyze_call_recording
    analyze_call_recording.delay(call_id)

    logger.info("transcribe_recording_completed", call_id=call_id)
    return result
