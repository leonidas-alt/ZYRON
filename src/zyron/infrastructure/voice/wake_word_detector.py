from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from zyron.infrastructure.voice.exceptions import WakeWordDetectionError


@dataclass(frozen=True, slots=True)
class WakeWordResult:
    detected: bool
    wake_word: str | None = None
    command: str = ""
    original_text: str = ""

    @property
    def has_command(self) -> bool:
        return bool(self.command.strip())


class WakeWordDetector:
    def __init__(
        self,
        wake_words: Iterable[str] | None = None,
    ) -> None:
        resolved_wake_words = tuple(
            word.strip()
            for word in (
                wake_words
                or (
                    "zyron",
                    "ei zyron",
                    "olá zyron",
                    "ola zyron",
                )
            )
            if word.strip()
        )

        if not resolved_wake_words:
            raise ValueError(
                "Pelo menos uma palavra de ativação deve ser informada."
            )

        self._wake_words = resolved_wake_words
        self._normalized_wake_words = tuple(
            sorted(
                {
                    self._normalize_text(word)
                    for word in resolved_wake_words
                },
                key=len,
                reverse=True,
            )
        )

    @property
    def wake_words(self) -> tuple[str, ...]:
        return self._wake_words

    def detect(
        self,
        text: str,
    ) -> WakeWordResult:
        original_text = text.strip()

        if not original_text:
            return WakeWordResult(
                detected=False,
                original_text="",
            )

        try:
            normalized_text = self._normalize_text(
                original_text
            )

            for wake_word in self._normalized_wake_words:
                match = self._find_wake_word(
                    normalized_text=normalized_text,
                    wake_word=wake_word,
                )

                if match is None:
                    continue

                command = self._extract_command(
                    original_text=original_text,
                    normalized_text=normalized_text,
                    match_start=match.start(),
                    match_end=match.end(),
                )

                return WakeWordResult(
                    detected=True,
                    wake_word=wake_word,
                    command=command,
                    original_text=original_text,
                )

            return WakeWordResult(
                detected=False,
                original_text=original_text,
            )
        except Exception as error:
            raise WakeWordDetectionError(
                "Não foi possível analisar a palavra de ativação."
            ) from error

    def is_detected(
        self,
        text: str,
    ) -> bool:
        return self.detect(text).detected

    def extract_command(
        self,
        text: str,
    ) -> str:
        result = self.detect(text)

        if not result.detected:
            return ""

        return result.command

    def _find_wake_word(
        self,
        normalized_text: str,
        wake_word: str,
    ) -> re.Match[str] | None:
        pattern = rf"(?<!\w){re.escape(wake_word)}(?!\w)"

        return re.search(
            pattern,
            normalized_text,
            flags=re.IGNORECASE,
        )

    def _extract_command(
        self,
        original_text: str,
        normalized_text: str,
        match_start: int,
        match_end: int,
    ) -> str:
        original_positions = self._build_original_positions(
            original_text
        )

        if not original_positions:
            return ""

        original_start = self._resolve_original_index(
            original_positions,
            match_start,
        )

        original_end = self._resolve_original_index(
            original_positions,
            match_end - 1,
        ) + 1

        before_wake_word = original_text[:original_start].strip()
        after_wake_word = original_text[original_end:].strip()

        after_wake_word = self._clean_command(
            after_wake_word
        )

        if after_wake_word:
            return after_wake_word

        before_wake_word = self._clean_command(
            before_wake_word
        )

        if self._is_only_activation_prefix(
            before_wake_word
        ):
            return ""

        return before_wake_word

    def _clean_command(
        self,
        text: str,
    ) -> str:
        cleaned_text = text.strip()

        cleaned_text = re.sub(
            r"^[\s,.:;!?—–\-]+",
            "",
            cleaned_text,
        )

        cleaned_text = re.sub(
            r"\s+",
            " ",
            cleaned_text,
        )

        return cleaned_text.strip()

    def _is_only_activation_prefix(
        self,
        text: str,
    ) -> bool:
        normalized_text = self._normalize_text(text)

        activation_prefixes = {
            "",
            "ei",
            "ola",
            "hey",
            "ok",
            "okay",
        }

        return normalized_text in activation_prefixes

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        decomposed_text = unicodedata.normalize(
            "NFKD",
            text.casefold(),
        )

        without_accents = "".join(
            character
            for character in decomposed_text
            if not unicodedata.combining(character)
        )

        normalized_spaces = re.sub(
            r"\s+",
            " ",
            without_accents,
        )

        return normalized_spaces.strip()

    def _build_original_positions(
        self,
        text: str,
    ) -> list[int]:
        positions: list[int] = []

        for index, character in enumerate(text):
            normalized_character = self._normalize_character(
                character
            )

            for _ in normalized_character:
                positions.append(index)

        return positions

    def _normalize_character(
        self,
        character: str,
    ) -> str:
        decomposed_character = unicodedata.normalize(
            "NFKD",
            character.casefold(),
        )

        return "".join(
            value
            for value in decomposed_character
            if not unicodedata.combining(value)
        )

    def _resolve_original_index(
        self,
        positions: list[int],
        normalized_index: int,
    ) -> int:
        if normalized_index < 0:
            return 0

        if normalized_index >= len(positions):
            return positions[-1]

        return positions[normalized_index]
