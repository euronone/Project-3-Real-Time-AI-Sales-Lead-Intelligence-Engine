"""Celery application configuration with Redis broker."""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "salesiq",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.tasks.transcription_tasks.*": {"queue": "transcription"},
        "app.tasks.analysis_tasks.*": {"queue": "analysis"},
        "app.tasks.prediction_tasks.*": {"queue": "prediction"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
    },
)

celery_app.autodiscover_tasks([
    "app.tasks.transcription_tasks",
    "app.tasks.analysis_tasks",
    "app.tasks.prediction_tasks",
    "app.tasks.notification_tasks",
])
