import logging

import deepl
import requests

from config import settings

logger = logging.getLogger(__name__)


class TranslationService:
    def translate(self, text: str, source: str, target: str) -> dict:
        """Traduce texto usando DeepL. Si falla, usa LibreTranslate como fallback."""
        if not text.strip():
            return {"translated": "", "provider": "none"}

        if settings.deepl_api_key:
            try:
                return self._deepl(text, source, target)
            except Exception as exc:
                logger.warning("DeepL falló (%s), usando LibreTranslate.", exc)

        return self._libretranslate(text, source, target)

    def _deepl(self, text: str, source: str, target: str) -> dict:
        translator = deepl.Translator(settings.deepl_api_key)
        # DeepL usa "EN-US" para inglés destino; acepta "ES" para español
        target_lang = "EN-US" if target.upper() == "EN" else target.upper()
        result = translator.translate_text(
            text,
            source_lang=source.upper(),
            target_lang=target_lang,
        )
        return {"translated": result.text, "provider": "deepl"}

    def _libretranslate(self, text: str, source: str, target: str) -> dict:
        response = requests.post(
            f"{settings.libretranslate_url}/translate",
            json={"q": text, "source": source.lower(), "target": target.lower()},
            timeout=10,
        )
        response.raise_for_status()
        return {"translated": response.json()["translatedText"], "provider": "libretranslate"}


translation_service = TranslationService()
