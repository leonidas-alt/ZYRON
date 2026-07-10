from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from domain.ports import AIClient, InteractionRepository, MemoryRepository, SpeechRecognizer, SpeechSynthesizer, WakeWordService
from domain.models import AssistantResponse, CommandIntent

class ApplicationLauncher(ABC):
    @abstractmethod
    async def open_application(self, app_name: str) -> None: ...
class BrowserGateway(ABC):
    @abstractmethod
    async def open_site(self, site: str) -> None: ...
    @abstractmethod
    async def google_search(self, query: str) -> None: ...
class TimeProvider(ABC):
    @abstractmethod
    def current_time_text(self) -> str: ...
class WeatherProvider(ABC):
    @abstractmethod
    async def current_temperature_text(self) -> str: ...
class CommandInterpreterPort(ABC):
    @abstractmethod
    def interpret(self, text: str) -> CommandIntent: ...
class AssistantCommand(ABC):
    @abstractmethod
    async def execute(self, intent: CommandIntent) -> AssistantResponse: ...
