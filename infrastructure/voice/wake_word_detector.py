from __future__ import annotations

import re

from application.ports import WakeWordDetectorPort


class TextWakeWordDetector(WakeWordDetectorPort):
    def __init__(self, wake_word: str = "zyron") -> None:
        self.wake_word = wake_word.strip().lower()

    def contains_wake_word(self, text: str) -> bool:
        return bool(re.search(rf"\b{re.escape(self.wake_word)}\b", text.lower()))

    def remove_wake_word(self, text: str) -> str:
        cleaned = re.sub(rf"\b{re.escape(self.wake_word)}\b[\s,;:.-]*", "", text, count=1, flags=re.IGNORECASE)
        return " ".join(cleaned.split()).strip()
