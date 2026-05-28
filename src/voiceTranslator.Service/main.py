from fastapi import FastAPI

from config import settings

app = FastAPI(title="Voice Translator Service", version="1.0.0")


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
