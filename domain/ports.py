from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from domain.models import AssistantResponse, CommandIntent, Interaction, MemoryItem, PluginMetadata, Skill


class PluginInterface(ABC):
    metadata: PluginMetadata

    @abstractmethod
    def skills(self) -> tuple[Skill, ...]:
        raise NotImplementedError

    @abstractmethod
    def can_handle(self, intent: CommandIntent) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        raise NotImplementedError


class AIClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError


class InteractionRepository(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_recent_interactions(self, limit: int = 5) -> list[Interaction]:
        raise NotImplementedError


class MemoryRepository(InteractionRepository):
    @abstractmethod
    async def remember(self, key: str, value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def recall(self, key: str) -> MemoryItem | None:
        raise NotImplementedError

    @abstractmethod
    async def list_memories(self) -> list[MemoryItem]:
        raise NotImplementedError

    @abstractmethod
    async def forget(self, key: str) -> bool:
        raise NotImplementedError


class SpeechRecognizer(ABC):
    @abstractmethod
    async def listen_once(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def transcribe(self, audio: Any) -> str:
        raise NotImplementedError


class SpeechSynthesizer(ABC):
    @abstractmethod
    async def speak(self, text: str) -> None:
        raise NotImplementedError


class WakeWordService(ABC):
    @abstractmethod
    def is_wake_word_present(self, text: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def remove_wake_word(self, text: str) -> str:
        raise NotImplementedError
