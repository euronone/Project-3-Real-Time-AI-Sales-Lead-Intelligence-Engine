"""Socket.IO server setup, room handlers, and emit helpers."""

import socketio
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

# Create Socket.IO server with Redis manager for horizontal scaling
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins,
    logger=False,
    engineio_logger=False,
)


@sio.event
async def connect(sid: str, environ: dict) -> bool:
    """Handle new Socket.IO connection."""
    logger.info("socketio_connect", sid=sid)
    return True


@sio.event
async def disconnect(sid: str) -> None:
    """Handle Socket.IO disconnection."""
    logger.info("socketio_disconnect", sid=sid)


@sio.event
async def join_call_room(sid: str, data: dict) -> None:
    """Agent joins a call's live room for real-time updates.

    Args:
        sid: Socket.IO session ID.
        data: Dict with 'call_id' key.
    """
    call_id = data.get("call_id")
    if call_id:
        room = f"call:{call_id}"
        sio.enter_room(sid, room)
        logger.info("socketio_join_room", sid=sid, room=room)
        await sio.emit("room_joined", {"call_id": call_id}, room=sid)


@sio.event
async def leave_call_room(sid: str, data: dict) -> None:
    """Agent leaves a call's live room.

    Args:
        sid: Socket.IO session ID.
        data: Dict with 'call_id' key.
    """
    call_id = data.get("call_id")
    if call_id:
        room = f"call:{call_id}"
        sio.leave_room(sid, room)
        logger.info("socketio_leave_room", sid=sid, room=room)


# --- Emit Helpers ---


async def emit_transcript_chunk(call_id: str, data: dict) -> None:
    """Emit a new transcript segment to the call room."""
    await sio.emit("transcript_chunk", data, room=f"call:{call_id}")


async def emit_ai_guidance(call_id: str, data: dict) -> None:
    """Emit real-time AI guidance to the call room."""
    await sio.emit("ai_guidance", data, room=f"call:{call_id}")


async def emit_sentiment_update(call_id: str, data: dict) -> None:
    """Emit a sentiment score update to the call room."""
    await sio.emit("sentiment_update", data, room=f"call:{call_id}")


async def emit_red_flag_alert(call_id: str, data: dict) -> None:
    """Emit a red flag alert to the call room."""
    await sio.emit("red_flag_alert", data, room=f"call:{call_id}")


async def emit_call_status_changed(call_id: str, data: dict) -> None:
    """Emit a call status change event."""
    await sio.emit("call_status_changed", data, room=f"call:{call_id}")


async def emit_notification(user_sid: str, data: dict) -> None:
    """Emit a notification to a specific user."""
    await sio.emit("notification", data, room=user_sid)


async def emit_deal_prediction_updated(call_id: str, data: dict) -> None:
    """Emit an updated deal prediction to the call room."""
    await sio.emit("deal_prediction_updated", data, room=f"call:{call_id}")
