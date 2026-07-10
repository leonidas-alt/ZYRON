from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AudioCapturePort(ABC):
    @abstractmethod
    async def capture(self) -> Any:
        raise NotImplementedError


class SpeechRecognizerPort(ABC):
    @abstractmethod
    async def transcribe(self, audio: Any) -> str:
        raise NotImplementedError


class SpeechSynthesizerPort(ABC):
    @abstractmethod
    async def speak(self, text: str) -> None:
        raise NotImplementedError


class WakeWordDetectorPort(ABC):
    @abstractmethod
    def contains_wake_word(self, text: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def remove_wake_word(self, text: str) -> str:
        raise NotImplementedError
