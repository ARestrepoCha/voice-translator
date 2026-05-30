import logging
import time
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice Translator Service", version="1.0.0")


@app.on_event("startup")
async def startup():
    from stt.whisper_service import whisper_service  # noqa: F401


# ── Models ────────────────────────────────────────────────────────────────────

class TranslateTextRequest(BaseModel):
    text: str
    source: str = "ES"
    target: str = "EN"


class ConfigUpdate(BaseModel):
    source_language: str | None = None
    target_language: str | None = None


class SynthesizeRequest(BaseModel):
    text: str
    voice: str | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/config")
async def get_config():
    return {
        "source_language": settings.source_language,
        "target_language": settings.target_language,
        "whisper_model": settings.whisper_model,
    }


@app.put("/config")
async def update_config(body: ConfigUpdate):
    if body.source_language:
        settings.source_language = body.source_language.upper()
    if body.target_language:
        settings.target_language = body.target_language.upper()
    return {
        "source_language": settings.source_language,
        "target_language": settings.target_language,
    }


@app.post("/transcribe")
async def transcribe(audio: UploadFile):
    if audio.content_type not in ("audio/wav", "audio/wave", "audio/x-wav", "application/octet-stream"):
        raise HTTPException(
            status_code=415,
            detail=f"Formato no soportado: {audio.content_type}. Usa audio/wav.",
        )

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Archivo de audio vacío.")

    from stt.whisper_service import whisper_service

    try:
        result = whisper_service.transcribe(audio_bytes, filename=audio.filename or "audio.wav")
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error al transcribir: {exc}") from exc

    return result


@app.post("/translate-text")
async def translate_text(body: TranslateTextRequest):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    from translation.translation_service import translation_service

    try:
        result = translation_service.translate(body.text, body.source, body.target)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error de traducción: {exc}") from exc

    return result


@app.get("/voices")
async def list_voices():
    from tts.tts_service import AVAILABLE_VOICES
    return {"voices": [{"id": k, **v} for k, v in AVAILABLE_VOICES.items()]}


@app.post("/synthesize")
async def synthesize(body: SynthesizeRequest):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    from tts.tts_service import tts_service

    try:
        audio_bytes = await tts_service.synthesize(body.text, body.voice)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error de síntesis: {exc}") from exc

    return Response(content=audio_bytes, media_type="audio/mpeg")


@app.post("/translate-audio")
async def translate_audio(audio: UploadFile):
    if audio.content_type not in ("audio/wav", "audio/wave", "audio/x-wav", "application/octet-stream"):
        raise HTTPException(
            status_code=415,
            detail=f"Formato no soportado: {audio.content_type}. Usa audio/wav.",
        )

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Archivo de audio vacío.")

    from stt.whisper_service import whisper_service
    from translation.translation_service import translation_service
    from tts.tts_service import tts_service

    total_start = time.perf_counter()

    # ── STT ──────────────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        stt_result = whisper_service.transcribe(audio_bytes, filename=audio.filename or "audio.wav")
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Error STT: {exc}") from exc
    stt_ms = int((time.perf_counter() - t0) * 1000)

    original_text = stt_result["text"]
    detected_lang = stt_result["language"].upper()
    logger.info("[STT] %dms | lang=%s | text=%s", stt_ms, detected_lang, original_text[:80])

    if not original_text.strip():
        raise HTTPException(status_code=422, detail="No se detectó voz en el audio.")

    # ── Traducción ───────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        trans_result = translation_service.translate(
            original_text,
            source=settings.source_language,
            target=settings.target_language,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error traducción: {exc}") from exc
    trans_ms = int((time.perf_counter() - t0) * 1000)

    translated_text = trans_result["translated"]
    logger.info("[TRANSLATION] %dms | provider=%s | text=%s", trans_ms, trans_result["provider"], translated_text[:80])

    # ── TTS ──────────────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    try:
        output_audio = await tts_service.synthesize(translated_text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error TTS: {exc}") from exc
    tts_ms = int((time.perf_counter() - t0) * 1000)

    total_ms = int((time.perf_counter() - total_start) * 1000)
    logger.info("[TTS] %dms | total=%dms", tts_ms, total_ms)

    return Response(
        content=output_audio,
        media_type="audio/mpeg",
        headers={
            "X-STT-Ms":          str(stt_ms),
            "X-Translation-Ms":  str(trans_ms),
            "X-TTS-Ms":          str(tts_ms),
            "X-Total-Ms":        str(total_ms),
            "X-Original-Text":   quote(original_text[:200]),
            "X-Translated-Text": quote(translated_text[:200]),
        },
    )
