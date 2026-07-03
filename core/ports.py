from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.models import AssistantResponse, CommandIntent


class AIClient(ABC):

    @abstractmethod
    async def generate(self, prompt: str) -> str:


class ApplicationLauncher(ABC):

    @abstractmethod
    async def open_application(self, app_name: str) -> None:


class BrowserGateway(ABC):

    @abstractmethod
    async def open_site(self, site: str) -> None:

    @abstractmethod
    async def google_search(self, query: str) -> None:


class TimeProvider(ABC):

    @abstractmethod
    def current_time_text(self) -> str:


class WeatherProvider(ABC):

    @abstractmethod
    async def current_temperature_text(self) -> str:


class InteractionRepository(ABC):

    @abstractmethod
    async def initialize(self) -> None:

    @abstractmethod
    async def save_interaction(self, user_text: str, assistant_text: str) -> None:


class SpeechRecognizer(ABC):

    @abstractmethod
    async def listen_once(self) -> Any:

    @abstractmethod
    async def transcribe(self, audio: Any) -> str:


class SpeechSynthesizer(ABC):

    @abstractmethod
    async def speak(self, text: str) -> None:

class WakeWordService(ABC):

    @abstractmethod
    def is_wake_word_present(self, text: str) -> bool:

    @abstractmethod
    def remove_wake_word(self, text: str) -> str:


class CommandInterpreterPort(ABC):

    @abstractmethod
    def interpret(self, text: str) -> CommandIntent:


class AssistantCommand(ABC):

    @abstractmethod
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
