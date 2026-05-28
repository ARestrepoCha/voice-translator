from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepl_api_key: str = ""
    libretranslate_url: str = "http://localhost:5000"

    source_language: str = "ES"
    target_language: str = "EN"

    whisper_model: str = "base"

    tts_voice_en: str = "en-US-JennyNeural"
    tts_voice_es: str = "es-CO-SalomeNeural"

    host: str = "localhost"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
