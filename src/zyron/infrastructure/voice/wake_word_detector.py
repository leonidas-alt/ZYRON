from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

from zyron.infrastructure.voice.exceptions import WakeWordDetectionError


class WakeWordDetector:
    def __init__(
        self,
        wake_words: Iterable[str],
    ) -> None:
        normalized_words = tuple(
            self._normalize(word)
            for word in wake_words
            if word.strip()
        )

        if not normalized_words:
            raise ValueError(
                "É necessário informar pelo menos uma palavra de ativação."
            )

        self._wake_words = normalized_words
        self._wake_word_aliases = {
            "zyron",
            "ziron",
            "siron",
            "ciron",
            "diron",
            "dirao",
            "zirao",
            "sirion",
        }

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

        normalized_text = self._normalize(text)

        if not normalized_text:
            return False

        words = normalized_text.split()

        return any(
            word in self._wake_word_aliases
            or word in self._wake_words
            for word in words
        )

    def extract_command(
        self,
        text: str,
    ) -> str:
        if not isinstance(text, str):
            raise WakeWordDetectionError(
                "O texto informado é inválido."
            )

        normalized_text = self._normalize(text)

        if not normalized_text:
            return ""

        words = normalized_text.split()

        for index, word in enumerate(words):
            if (
                word in self._wake_word_aliases
                or word in self._wake_words
            ):
                return " ".join(
                    words[index + 1:]
                ).strip()

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

    def _normalize(
        self,
        text: str,
    ) -> str:
        cleaned_text = "".join(
            character
            for character in text
            if character.isprintable()
        )

        cleaned_text = unicodedata.normalize(
            "NFD",
            cleaned_text,
        )

        cleaned_text = "".join(
            character
            for character in cleaned_text
            if unicodedata.category(character) != "Mn"
        )

        cleaned_text = cleaned_text.casefold()

        cleaned_text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            cleaned_text,
        )

        cleaned_text = re.sub(
            r"\s+",
            " ",
            cleaned_text,
        )

        return cleaned_text.strip()