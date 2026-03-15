"""Twilio service: voice call management and webhook handling."""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.call import Call, CallStatus

logger = structlog.get_logger(__name__)


class TwilioService:
    """Wraps Twilio Voice SDK for call management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER

    async def make_call(self, to_number: str, call_id: str) -> str:
        """Initiate an outbound call via Twilio.

        Args:
            to_number: The phone number to call.
            call_id: Internal call ID for callback reference.

        Returns:
            Twilio Call SID.
        """
        # In production, use the Twilio client:
        # from twilio.rest import Client
        # client = Client(self.account_sid, self.auth_token)
        # twilio_call = client.calls.create(
        #     to=to_number,
        #     from_=self.phone_number,
        #     url=f"{settings.APP_BASE_URL}/api/v1/twilio/voice",
        #     status_callback=f"{settings.APP_BASE_URL}/api/v1/twilio/status",
        #     record=True,
        # )
        # return twilio_call.sid
        logger.info("twilio_make_call", to=to_number, call_id=call_id)
        return f"CA_stub_{call_id}"

    async def get_token(self, identity: str) -> str:
        """Generate a Twilio capability token for the client SDK.

        Args:
            identity: The user identity for the token.

        Returns:
            JWT token string for Twilio Client SDK.
        """
        # In production:
        # from twilio.jwt.access_token import AccessToken
        # from twilio.jwt.access_token.grants import VoiceGrant
        # token = AccessToken(self.account_sid, settings.TWILIO_API_KEY_SID,
        #                     settings.TWILIO_API_KEY_SECRET, identity=identity)
        # voice_grant = VoiceGrant(outgoing_application_sid="...", incoming_allow=True)
        # token.add_grant(voice_grant)
        # return token.to_jwt()
        logger.info("twilio_get_token", identity=identity)
        return f"stub_token_{identity}"

    async def handle_voice_webhook(self, form_data: dict) -> str:
        """Handle Twilio voice webhook and return TwiML.

        Args:
            form_data: Form data from Twilio webhook.

        Returns:
            TwiML XML string.
        """
        call_sid = form_data.get("CallSid", "")
        logger.info("twilio_voice_webhook", call_sid=call_sid)

        # Return TwiML that connects the call and starts a media stream
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://your-server.com/api/v1/twilio/media-stream" />
    </Connect>
</Response>"""
        return twiml

    async def handle_status_callback(self, form_data: dict) -> None:
        """Handle Twilio call status callback.

        Args:
            form_data: Form data from Twilio status webhook.
        """
        call_sid = form_data.get("CallSid", "")
        call_status = form_data.get("CallStatus", "")
        duration = form_data.get("CallDuration")

        logger.info(
            "twilio_status_callback",
            call_sid=call_sid,
            status=call_status,
        )

        # Update call status in DB
        status_map = {
            "initiated": CallStatus.INITIATED,
            "ringing": CallStatus.RINGING,
            "in-progress": CallStatus.IN_PROGRESS,
            "completed": CallStatus.COMPLETED,
            "failed": CallStatus.FAILED,
            "no-answer": CallStatus.NO_ANSWER,
        }

        result = await self.db.execute(
            select(Call).where(Call.twilio_call_sid == call_sid)
        )
        call = result.scalar_one_or_none()
        if call and call_status in status_map:
            call.status = status_map[call_status]
            if duration:
                call.duration_seconds = int(duration)
            await self.db.flush()

    async def handle_recording_callback(self, form_data: dict) -> None:
        """Handle Twilio recording completed callback.

        Args:
            form_data: Form data from Twilio recording webhook.
        """
        call_sid = form_data.get("CallSid", "")
        recording_sid = form_data.get("RecordingSid", "")
        recording_url = form_data.get("RecordingUrl", "")

        logger.info(
            "twilio_recording_callback",
            call_sid=call_sid,
            recording_sid=recording_sid,
        )

        result = await self.db.execute(
            select(Call).where(Call.twilio_call_sid == call_sid)
        )
        call = result.scalar_one_or_none()
        if call:
            call.recording_sid = recording_sid
            call.recording_url = recording_url
            await self.db.flush()

            # Trigger async transcription task
            from app.tasks.transcription_tasks import transcribe_recording
            transcribe_recording.delay(str(call.id), recording_url)
