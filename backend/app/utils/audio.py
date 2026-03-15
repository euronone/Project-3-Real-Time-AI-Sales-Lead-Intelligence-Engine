"""Audio format conversion helpers."""

import audioop
import io
import struct
import wave


def convert_mulaw_to_wav(
    mulaw_data: bytes,
    sample_rate: int = 8000,
    channels: int = 1,
    sample_width: int = 2,
) -> bytes:
    """Convert mu-law encoded audio to WAV format.

    Twilio Media Streams send audio as base64-encoded mu-law at 8kHz.
    This function converts it to standard PCM WAV for Whisper API.

    Args:
        mulaw_data: Raw mu-law encoded audio bytes.
        sample_rate: Audio sample rate in Hz (default: 8000 for Twilio).
        channels: Number of audio channels (default: 1 mono).
        sample_width: Output sample width in bytes (default: 2 for 16-bit).

    Returns:
        WAV file content as bytes.
    """
    # Decode mu-law to linear PCM
    pcm_data = audioop.ulaw2lin(mulaw_data, sample_width)

    # Write to WAV format in memory
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)

    return buffer.getvalue()


def chunk_audio(
    audio_data: bytes,
    chunk_duration_ms: int = 500,
    sample_rate: int = 8000,
    sample_width: int = 1,
) -> list[bytes]:
    """Split audio data into fixed-duration chunks.

    Args:
        audio_data: Raw audio bytes.
        chunk_duration_ms: Duration of each chunk in milliseconds.
        sample_rate: Audio sample rate in Hz.
        sample_width: Sample width in bytes.

    Returns:
        List of audio byte chunks.
    """
    bytes_per_ms = (sample_rate * sample_width) / 1000
    chunk_size = int(bytes_per_ms * chunk_duration_ms)

    chunks = []
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i : i + chunk_size]
        if len(chunk) > 0:
            chunks.append(chunk)

    return chunks
