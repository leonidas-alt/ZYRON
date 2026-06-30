"""Command routing and execution layer."""

from ai.ollama_client import OllamaClient
from automation.app_launcher import AppLauncher
from automation.browser_controller import BrowserController
from core.models import AssistantResponse, CommandIntent, CommandType
from services.time_service import TimeService
from services.weather_service import WeatherService


class CommandRouter:
    """Executes interpreted intents through the proper service or automation adapter."""

    def __init__(self, ai_client: OllamaClient, app_launcher: AppLauncher, browser_controller: BrowserController, time_service: TimeService, weather_service: WeatherService) -> None:
        """Receive all executable dependencies used by command handlers."""
        self.ai_client = ai_client
        self.app_launcher = app_launcher
        self.browser_controller = browser_controller
        self.time_service = time_service
        self.weather_service = weather_service

    def route(self, intent: CommandIntent) -> AssistantResponse:
        """Dispatch an intent to its handler and return a response."""
        if intent.command_type == CommandType.OPEN_APP and intent.target:
            self.app_launcher.open_application(intent.target)
            return AssistantResponse(f"Abrindo {intent.target}.")
        if intent.command_type == CommandType.OPEN_SITE and intent.target:
            self.browser_controller.open_site(intent.target)
            return AssistantResponse(f"Abrindo o site {intent.target}.")
        if intent.command_type == CommandType.GOOGLE_SEARCH and intent.target:
            self.browser_controller.google_search(intent.target)
            return AssistantResponse(f"Pesquisando por {intent.target}.")
        if intent.command_type == CommandType.CURRENT_TIME:
            return AssistantResponse(f"Agora são {self.time_service.current_time_text()}.")
        if intent.command_type == CommandType.CURRENT_WEATHER:
            return AssistantResponse(f"A temperatura atual é {self.weather_service.current_temperature_text()}.")
        if intent.command_type == CommandType.AI_CHAT:
            return AssistantResponse(self.ai_client.generate(intent.raw_text))
        return AssistantResponse("Não entendi o comando. Pode repetir?")
