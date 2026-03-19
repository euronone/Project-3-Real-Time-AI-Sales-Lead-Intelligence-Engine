"""WebSocket handler for Twilio Media Stream audio chunks."""

import base64
import json

import structlog
from fastapi import WebSocket

from app.utils.audio import convert_mulaw_to_wav

logger = structlog.get_logger(__name__)


class CallStreamHandler:
    """Handles a Twilio Media Stream WebSocket connection.

    Receives audio chunks from Twilio, buffers them, and feeds them
    through the AI pipeline for real-time transcription and analysis.
    """

    def __init__(self) -> None:
        self.call_id: str | None = None
        self.stream_sid: str | None = None
        self.audio_buffer: bytearray = bytearray()
        self.chunk_index: int = 0
        self.transcript_context: str = ""

    async def handle_stream(self, websocket: WebSocket) -> None:
        """Main loop for processing Twilio Media Stream messages.

        Args:
            websocket: The WebSocket connection from Twilio.
        """
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            event_type = data.get("event")

            if event_type == "connected":
                logger.info("media_stream_connected")

            elif event_type == "start":
                self.stream_sid = data.get("streamSid")
                start_data = data.get("start", {})
                self.call_id = start_data.get("callSid")
                logger.info(
                    "media_stream_started",
                    stream_sid=self.stream_sid,
                    call_id=self.call_id,
                )

            elif event_type == "media":
                media = data.get("media", {})
                payload = media.get("payload", "")
                audio_bytes = base64.b64decode(payload)
                self.audio_buffer.extend(audio_bytes)

                # Process when buffer reaches ~0.5 seconds of audio (8000 bytes at 8kHz mulaw)
                if len(self.audio_buffer) >= 8000:
                    await self._process_audio_buffer()

            elif event_type == "stop":
                # Process any remaining audio
                if self.audio_buffer:
                    await self._process_audio_buffer()
                logger.info("media_stream_stopped", call_id=self.call_id)
                break

    async def _process_audio_buffer(self) -> None:
        """Process the buffered audio through the AI pipeline."""
        if not self.call_id:
            self.audio_buffer.clear()
            return

        # Convert mulaw to wav
        convert_mulaw_to_wav(bytes(self.audio_buffer))
        self.audio_buffer.clear()
        self.chunk_index += 1

        # In production, this would call the AI pipeline:
        # from app.ai.pipeline import AIPipeline
        # pipeline = AIPipeline(db_session)
        # result = await pipeline.process_audio_chunk(
        #     call_id=uuid.UUID(self.call_id),
        #     audio_chunk=wav_data,
        #     chunk_index=self.chunk_index,
        #     transcript_context=self.transcript_context,
        # )

        # Emit results to Socket.IO
        # if result.get("transcript"):
        #     await emit_transcript_chunk(self.call_id, result["transcript"])
        #     self.transcript_context += f"\n{result['transcript']['text']}"
        # if result.get("analysis"):
        #     await emit_sentiment_update(self.call_id, result["analysis"])
        # if result.get("guidance"):
        #     await emit_ai_guidance(self.call_id, result["guidance"])

        logger.debug(
            "audio_chunk_processed",
            call_id=self.call_id,
            chunk_index=self.chunk_index,
        )

    async def cleanup(self) -> None:
        """Clean up resources when the stream ends."""
        self.audio_buffer.clear()
        logger.info("media_stream_cleanup", call_id=self.call_id)
