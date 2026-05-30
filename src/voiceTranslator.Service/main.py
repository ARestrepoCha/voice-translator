import logging

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from config import settings

logging.basicConfig(level=logging.INFO)

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
