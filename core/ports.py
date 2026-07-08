from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from core.models import AssistantResponse, CommandIntent, Interaction


class AIClient(ABC):

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError


class ApplicationLauncher(ABC):

    @abstractmethod
    async def open_application(self, app_name: str) -> None:
        raise NotImplementedError


class BrowserGateway(ABC):

    @abstractmethod
    async def open_site(self, site: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def google_search(self, query: str) -> None:
        raise NotImplementedError


class TimeProvider(ABC):

    @abstractmethod
    def current_time_text(self) -> str:
        raise NotImplementedError


class WeatherProvider(ABC):

    @abstractmethod
    async def current_temperature_text(self) -> str:
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


class CommandInterpreterPort(ABC):

    @abstractmethod
    def interpret(self, text: str) -> CommandIntent:
        raise NotImplementedError


class AssistantCommand(ABC):

    @abstractmethod
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        raise NotImplementedError
