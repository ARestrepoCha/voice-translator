import logging
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

from config import settings

logger = logging.getLogger(__name__)


class WhisperService:
    def __init__(self):
        logger.info("Cargando modelo Whisper '%s'...", settings.whisper_model)
        self._model = WhisperModel(
            settings.whisper_model,
            device="cpu",
            compute_type="int8",
        )
        logger.info("Modelo Whisper listo.")

    def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> dict:
        suffix = Path(filename).suffix or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            segments, info = self._model.transcribe(tmp_path, beam_size=5)
            text = " ".join(seg.text for seg in segments).strip()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        return {
            "text": text,
            "language": info.language,
            "duration_ms": int(info.duration * 1000),
        }


# Singleton — cargado una vez al importar el módulo
whisper_service = WhisperService()
