"""Text-to-speech: OpenAI TTS with gTTS fallback (Arabic)."""
import base64
import uuid
from pathlib import Path

from flask import current_app


def _openai_tts(text: str, voice: str) -> bytes | None:
    api_key = current_app.config.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        resp = client.audio.speech.create(
            model="tts-1",
            voice=voice or "nova",
            input=text[:4096],
        )
        return resp.content
    except Exception:
        return None


def _gtts_tts(text: str, lang: str) -> bytes | None:
    try:
        from gtts import gTTS
        import io

        tts = gTTS(text=text[:4096], lang=lang or "ar", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None


def synthesize(
    text: str,
    *,
    lang: str = "ar",
    voice: str = "nova",
    save_file: bool = True,
) -> dict:
    """
    Returns dict with audio_base64, format, source, and optional url/filename.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("النص فارغ")
    if len(text) > 4096:
        text = text[:4096]

    audio_bytes = _openai_tts(text, voice)
    source = "openai"

    if not audio_bytes:
        audio_bytes = _gtts_tts(text, lang)
        source = "gtts"

    if not audio_bytes:
        raise RuntimeError("تعذر توليد الصوت. ثبّت gTTS: pip install gTTS")

    result = {
        "source": source,
        "format": "mp3",
        "audio_base64": base64.b64encode(audio_bytes).decode("ascii"),
        "char_count": len(text),
    }

    if save_file:
        tts_dir = Path(current_app.config["TTS_FOLDER"])
        tts_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.mp3"
        path = tts_dir / filename
        path.write_bytes(audio_bytes)
        result["filename"] = filename
        result["url"] = f"/api/ai/tts/audio/{filename}"

    return result
