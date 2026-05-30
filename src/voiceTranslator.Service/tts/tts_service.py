import logging

import edge_tts

from config import settings

logger = logging.getLogger(__name__)

AVAILABLE_VOICES = {
    "en-US-JennyNeural":  {"lang": "EN", "gender": "Female"},
    "en-US-GuyNeural":    {"lang": "EN", "gender": "Male"},
    "es-CO-SalomeNeural": {"lang": "ES", "gender": "Female"},
    "es-ES-AlvaroNeural": {"lang": "ES", "gender": "Male"},
}


class TTSService:
    def default_voice_for(self, language: str) -> str:
        if language.upper().startswith("ES"):
            return settings.tts_voice_es
        return settings.tts_voice_en

    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        selected = voice or self.default_voice_for(settings.target_language)
        if selected not in AVAILABLE_VOICES:
            raise ValueError(f"Voz no soportada: '{selected}'. Opciones: {list(AVAILABLE_VOICES)}")

        logger.info("Sintetizando con voz '%s': %s", selected, text[:60])
        communicate = edge_tts.Communicate(text, voice=selected)

        audio_chunks: list[bytes] = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        return b"".join(audio_chunks)


tts_service = TTSService()
