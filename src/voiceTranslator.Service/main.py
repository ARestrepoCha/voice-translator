import logging

from fastapi import FastAPI, HTTPException, UploadFile

from config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Voice Translator Service", version="1.0.0")


@app.on_event("startup")
async def startup():
    # Importar aquí fuerza la carga del modelo al arrancar, no en el primer request
    from stt.whisper_service import whisper_service  # noqa: F401


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
