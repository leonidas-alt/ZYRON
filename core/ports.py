from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from core.models import AssistantResponse, CommandIntent


class AIClient(ABC):
    """Contract for text-generation providers."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt."""


class ApplicationLauncher(ABC):
    """Contract for desktop application launchers."""

    @abstractmethod
    async def open_application(self, app_name: str) -> None:
        """Open an application by name or path."""


class BrowserGateway(ABC):
    """Contract for browser automation providers."""

    @abstractmethod
    async def open_site(self, site: str) -> None:
        """Open a web site."""

    @abstractmethod
    async def google_search(self, query: str) -> None:
        """Open a Google search for a query."""


class TimeProvider(ABC):
    """Contract for time providers."""

    @abstractmethod
    def current_time_text(self) -> str:
        """Return the current time formatted for speech."""


class WeatherProvider(ABC):
    """Contract for weather providers."""

    @abstractmethod
    async def current_temperature_text(self) -> str:
        """Return the current temperature formatted for speech."""


class InteractionRepository(ABC):
    """Contract for assistant interaction persistence."""

    @abstractmethod
    async def initialize(self) -> None:
        """Prepare repository resources."""

    @abstractmethod
    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        """Persist an assistant interaction."""


class SpeechRecognizer(ABC):
    """Contract for speech-to-text adapters."""

    @abstractmethod
    async def listen_once(self) -> Any:
        """Capture one audio payload."""

    @abstractmethod
    async def transcribe(self, audio: Any) -> str:
        """Transcribe an audio payload."""


class SpeechSynthesizer(ABC):
    """Contract for text-to-speech adapters."""

    @abstractmethod
    async def speak(self, text: str) -> None:
        """Speak a text response."""


class WakeWordService(ABC):
    """Contract for wake-word detection."""

    @abstractmethod
    def is_wake_word_present(self, text: str) -> bool:
        """Return whether the wake word appears in text."""

    @abstractmethod
    def remove_wake_word(self, text: str) -> str:
        """Remove the wake word from text."""


class CommandInterpreterPort(ABC):
    """Contract for natural-language command interpretation."""

    @abstractmethod
    def interpret(self, text: str) -> CommandIntent:
        """Convert text to a command intent."""


class AssistantCommand(ABC):
    """Command Pattern contract for executable assistant actions."""

    @abstractmethod
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        """Execute a command intent."""
