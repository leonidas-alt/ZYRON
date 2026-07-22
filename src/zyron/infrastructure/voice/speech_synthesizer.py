from __future__ import annotations

import asyncio
from threading import Lock
from typing import Any

from zyron.infrastructure.voice.exceptions import SpeechSynthesisError


class SpeechSynthesizer:
    def __init__(
        self,
        rate: int = 180,
        volume: float = 1.0,
        voice_name: str | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError(
                "A velocidade da voz deve ser maior que zero."
            )

        if not 0.0 <= volume <= 1.0:
            raise ValueError(
                "O volume deve estar entre 0.0 e 1.0."
            )

        self._rate = rate
        self._volume = volume
        self._voice_name = voice_name
        self._engine: Any | None = None
        self._lock = Lock()

    async def speak(
        self,
        text: str,
    ) -> None:
        cleaned_text = text.strip()

        if not cleaned_text:
            return

        await asyncio.to_thread(
            self._speak_sync,
            cleaned_text,
        )

    def speak_sync(
        self,
        text: str,
    ) -> None:
        cleaned_text = text.strip()

        if not cleaned_text:
            return

        self._speak_sync(cleaned_text)

    def stop(self) -> None:
        if self._engine is None:
            return

        try:
            self._engine.stop()
        except Exception as error:
            raise SpeechSynthesisError(
                "Não foi possível interromper a reprodução de voz."
            ) from error

    def list_voices(self) -> list[str]:
        engine = self._get_engine()

        try:
            voices = engine.getProperty("voices")
        except Exception as error:
            raise SpeechSynthesisError(
                "Não foi possível consultar as vozes disponíveis."
            ) from error

        return [
            self._get_voice_description(voice)
            for voice in voices
        ]

    def _speak_sync(
        self,
        text: str,
    ) -> None:
        with self._lock:
            engine = self._get_engine()

            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as error:
                raise SpeechSynthesisError(
                    "Não foi possível reproduzir a resposta por voz."
                ) from error

    def _get_engine(self) -> Any:
        if self._engine is not None:
            return self._engine

        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
            engine.setProperty("volume", self._volume)

            if self._voice_name:
                self._select_voice(
                    engine=engine,
                    voice_name=self._voice_name,
                )

            self._engine = engine
            return engine
        except ImportError as error:
            raise SpeechSynthesisError(
                "A biblioteca pyttsx3 não está instalada."
            ) from error
        except Exception as error:
            raise SpeechSynthesisError(
                "Não foi possível inicializar o sintetizador de voz."
            ) from error

    def _select_voice(
        self,
        engine: Any,
        voice_name: str,
    ) -> None:
        normalized_name = voice_name.casefold()
        voices = engine.getProperty("voices")

        for voice in voices:
            voice_data = self._get_voice_description(
                voice
            ).casefold()

            if normalized_name in voice_data:
                engine.setProperty(
                    "voice",
                    voice.id,
                )
                return

        raise SpeechSynthesisError(
            f"A voz '{voice_name}' não foi encontrada."
        )

    def _get_voice_description(
        self,
        voice: Any,
    ) -> str:
        voice_id = str(
            getattr(
                voice,
                "id",
                "",
            )
        ).strip()

        voice_name = str(
            getattr(
                voice,
                "name",
                "",
            )
        ).strip()

        languages = getattr(
            voice,
            "languages",
            [],
        )

        language_text = ", ".join(
            self._normalize_language(language)
            for language in languages
        )

        values = [
            value
            for value in (
                voice_name,
                voice_id,
                language_text,
            )
            if value
        ]

        return " | ".join(values)

    def _normalize_language(
        self,
        language: object,
    ) -> str:
        if isinstance(
            language,
            bytes,
        ):
            return language.decode(
                "utf-8",
                errors="ignore",
            ).strip()

        return str(language).strip()
