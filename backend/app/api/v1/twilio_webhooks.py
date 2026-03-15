"""Twilio inbound webhooks: voice, status, recording callbacks and media stream."""

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.twilio_service import TwilioService
from app.realtime.call_stream_handler import CallStreamHandler

router = APIRouter()


@router.post("/voice")
async def twilio_voice_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Twilio voice webhook — returns TwiML response for call handling."""
    form_data = await request.form()
    service = TwilioService(db)
    twiml = await service.handle_voice_webhook(dict(form_data))
    return Response(content=twiml, media_type="application/xml")


@router.post("/status")
async def twilio_status_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Twilio call status callback — updates call status in DB."""
    form_data = await request.form()
    service = TwilioService(db)
    await service.handle_status_callback(dict(form_data))
    return {"status": "ok"}


@router.post("/recording")
async def twilio_recording_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Twilio recording completed callback — triggers transcription."""
    form_data = await request.form()
    service = TwilioService(db)
    await service.handle_recording_callback(dict(form_data))
    return {"status": "ok"}


@router.websocket("/media-stream")
async def twilio_media_stream(websocket: WebSocket) -> None:
    """WebSocket endpoint for Twilio Media Stream audio chunks."""
    await websocket.accept()
    handler = CallStreamHandler()
    try:
        await handler.handle_stream(websocket)
    except WebSocketDisconnect:
        await handler.cleanup()
