"""Celery tasks for async notification dispatch."""

import asyncio

import httpx
import structlog

from app.tasks.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.notification_tasks.send_notification_email", bind=True)
def send_notification_email(
    self,
    to_email: str,
    subject: str,
    body: str,
) -> dict:
    """Send a notification email asynchronously.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body: Email body content (HTML or plain text).

    Returns:
        Dict with send status.
    """
    logger.info("send_notification_email_started", to=to_email, subject=subject)

    # In production, integrate with an email service (SES, SendGrid, etc.)
    # import boto3
    # ses = boto3.client("ses")
    # ses.send_email(
    #     Source="noreply@salesiq.io",
    #     Destination={"ToAddresses": [to_email]},
    #     Message={
    #         "Subject": {"Data": subject},
    #         "Body": {"Html": {"Data": body}},
    #     },
    # )

    logger.info("send_notification_email_completed", to=to_email)
    return {"to": to_email, "status": "sent"}


@celery_app.task(name="app.tasks.notification_tasks.dispatch_webhook", bind=True)
def dispatch_webhook(
    self,
    webhook_url: str,
    event_type: str,
    payload: dict,
    secret: str | None = None,
) -> dict:
    """Dispatch an event to an outbound webhook.

    Args:
        webhook_url: The webhook endpoint URL.
        event_type: The event type being dispatched.
        payload: The event payload data.
        secret: Optional webhook secret for signature verification.

    Returns:
        Dict with dispatch status.
    """
    logger.info(
        "dispatch_webhook_started",
        url=webhook_url,
        event_type=event_type,
    )

    async def _run() -> dict:
        headers = {"Content-Type": "application/json"}
        if secret:
            headers["X-Webhook-Secret"] = secret

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    webhook_url,
                    json={"event": event_type, "data": payload},
                    headers=headers,
                )
                return {
                    "url": webhook_url,
                    "status_code": response.status_code,
                    "status": "delivered",
                }
            except Exception as e:
                logger.error(
                    "dispatch_webhook_failed",
                    url=webhook_url,
                    error=str(e),
                )
                return {
                    "url": webhook_url,
                    "status": "failed",
                    "error": str(e),
                }

    result = asyncio.get_event_loop().run_until_complete(_run())
    logger.info("dispatch_webhook_completed", url=webhook_url)
    return result
