"""Redis pub/sub publisher and subscriber that bridges events to Socket.IO."""

import json

import redis.asyncio as redis
import structlog

from app.config import settings
from app.realtime.socket_manager import (
    emit_ai_guidance,
    emit_call_status_changed,
    emit_deal_prediction_updated,
    emit_notification,
    emit_red_flag_alert,
    emit_sentiment_update,
    emit_transcript_chunk,
)

logger = structlog.get_logger(__name__)

CHANNEL_PREFIX = "salesiq:"


class EventPublisher:
    """Publishes events to Redis pub/sub channels."""

    def __init__(self) -> None:
        self.redis = redis.from_url(settings.REDIS_URL)

    async def publish(self, channel: str, event_type: str, data: dict) -> None:
        """Publish an event to a Redis channel.

        Args:
            channel: The channel name (e.g., 'call:abc123').
            event_type: The event type (e.g., 'transcript_chunk').
            data: The event payload.
        """
        message = json.dumps({"event": event_type, "data": data})
        await self.redis.publish(f"{CHANNEL_PREFIX}{channel}", message)
        logger.debug("event_published", channel=channel, event_type=event_type)

    async def close(self) -> None:
        """Close the Redis connection."""
        await self.redis.close()


class EventSubscriber:
    """Subscribes to Redis pub/sub and bridges events to Socket.IO."""

    def __init__(self) -> None:
        self.redis = redis.from_url(settings.REDIS_URL)
        self.pubsub = self.redis.pubsub()
        self._running = False

    async def start(self) -> None:
        """Start listening for events on Redis pub/sub."""
        await self.pubsub.psubscribe(f"{CHANNEL_PREFIX}*")
        self._running = True
        logger.info("event_subscriber_started")

        while self._running:
            message = await self.pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message.get("type") == "pmessage":
                await self._handle_message(message)

    async def _handle_message(self, message: dict) -> None:
        """Route a Redis pub/sub message to the appropriate Socket.IO emitter."""
        try:
            channel = message.get("channel", b"").decode()
            raw_data = message.get("data", b"").decode()
            payload = json.loads(raw_data)

            event_type = payload.get("event")
            data = payload.get("data", {})

            # Extract call_id from channel (e.g., "salesiq:call:abc123")
            parts = channel.replace(CHANNEL_PREFIX, "").split(":")
            parts[0] if parts else ""
            entity_id = parts[1] if len(parts) > 1 else ""

            event_handlers = {
                "transcript_chunk": lambda: emit_transcript_chunk(entity_id, data),
                "ai_guidance": lambda: emit_ai_guidance(entity_id, data),
                "sentiment_update": lambda: emit_sentiment_update(entity_id, data),
                "red_flag_alert": lambda: emit_red_flag_alert(entity_id, data),
                "call_status_changed": lambda: emit_call_status_changed(entity_id, data),
                "deal_prediction_updated": lambda: emit_deal_prediction_updated(entity_id, data),
                "notification": lambda: emit_notification(entity_id, data),
            }

            handler = event_handlers.get(event_type)
            if handler:
                await handler()

        except Exception as e:
            logger.error("event_subscriber_error", error=str(e))

    async def stop(self) -> None:
        """Stop the event subscriber."""
        self._running = False
        await self.pubsub.unsubscribe()
        await self.redis.close()
        logger.info("event_subscriber_stopped")
