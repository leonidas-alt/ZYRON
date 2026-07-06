from __future__ import annotations
from core.ports import WakeWordService

class WakeWordDetector(WakeWordService):

    def __init__(self, wake_word: str) -> None:
        self.wake_word = wake_word.lower().strip()

    def is_wake_word_present(self, text: str) -> bool:
        return self.wake_word in text.lower()

    def remove_wake_word(self, text: str) -> str:
        return text.lower().replace(self.wake_word, "", 1).strip(" ,.!?")
