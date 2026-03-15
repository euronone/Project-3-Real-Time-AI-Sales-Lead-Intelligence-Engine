"""OpenAI client wrapper for GPT-4o and Whisper API."""

import json
from typing import AsyncIterator

import structlog
from openai import AsyncOpenAI

from app.config import settings

logger = structlog.get_logger(__name__)


class OpenAIClient:
    """Wrapper around the OpenAI Python SDK for chat completions and Whisper."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.whisper_model = settings.OPENAI_WHISPER_MODEL

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: str | None = None,
    ) -> dict:
        """Send a chat completion request to GPT-4o.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens in response.
            response_format: If 'json', request JSON output.

        Returns:
            Parsed response content as dict.
        """
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""

            if response_format == "json":
                return json.loads(content)
            return {"content": content}

        except Exception as e:
            logger.error("openai_chat_completion_error", error=str(e))
            return {}

    async def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        """Stream a chat completion response from GPT-4o.

        Args:
            messages: List of message dicts.
            temperature: Sampling temperature.

        Yields:
            Content delta strings as they arrive.
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content

        except Exception as e:
            logger.error("openai_stream_error", error=str(e))

    async def whisper_transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
    ) -> dict:
        """Transcribe audio using OpenAI Whisper API.

        Args:
            audio_data: Raw audio bytes.
            language: Language code for transcription.

        Returns:
            Dict with text, start_time, end_time, confidence.
        """
        try:
            # Create a file-like object for the API
            import io

            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"

            transcript = await self.client.audio.transcriptions.create(
                model=self.whisper_model,
                file=audio_file,
                language=language,
                response_format="verbose_json",
            )

            return {
                "text": transcript.text,
                "start_time": 0.0,
                "end_time": getattr(transcript, "duration", 0.0),
                "confidence": 0.95,
            }

        except Exception as e:
            logger.error("openai_whisper_error", error=str(e))
            return {"text": "", "start_time": 0.0, "end_time": 0.0, "confidence": 0.0}
