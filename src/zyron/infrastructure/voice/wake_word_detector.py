from __future__ import annotations

from collections.abc import Iterable

from zyron.infrastructure.voice.exceptions import WakeWordDetectionError


class WakeWordDetector:
    def __init__(
        self,
        wake_words: Iterable[str],
    ) -> None:
        normalized_words = tuple(
            word.strip().casefold()
            for word in wake_words
            if word.strip()
        )

        if not normalized_words:
            raise ValueError(
                "É necessário informar pelo menos uma palavra de ativação."
            )

        self._wake_words = normalized_words

    @property
    def wake_words(self) -> tuple[str, ...]:
        return self._wake_words

    def detect(
        self,
        text: str,
    ) -> bool:
        if not isinstance(text, str):
            raise WakeWordDetectionError(
                "O texto informado é inválido."
            )

        normalized_text = text.strip().casefold()

        if not normalized_text:
            return False

        return any(
            wake_word in normalized_text
            for wake_word in self._wake_words
        )

    def extract_command(
        self,
        text: str,
    ) -> str:
        if not isinstance(text, str):
            raise WakeWordDetectionError(
                "O texto informado é inválido."
            )

        normalized_text = text.strip()

        if not normalized_text:
            return ""

        lowered_text = normalized_text.casefold()

        for wake_word in self._wake_words:
            index = lowered_text.find(wake_word)

            if index == -1:
                continue

            command = normalized_text[
                index + len(wake_word):
            ].strip(" ,.:;!?")

            return command

        return ""

    def require_wake_word(
        self,
        text: str,
    ) -> str:
        if not self.detect(text):
            raise WakeWordDetectionError(
                "Nenhuma palavra de ativação foi detectada."
            )

        return self.extract_command(text)
