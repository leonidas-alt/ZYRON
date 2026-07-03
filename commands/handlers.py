from __future__ import annotations

from core.models import AssistantResponse, CommandIntent
from core.ports import (
    AIClient,
    ApplicationLauncher,
    AssistantCommand,
    BrowserGateway,
    TimeProvider,
    WeatherProvider,
)


class OpenApplicationCommand(AssistantCommand):
    def __init__(self, app_launcher: ApplicationLauncher) -> None:
        self._app_launcher = app_launcher

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        if not intent.target:
            return AssistantResponse("Qual aplicativo devo abrir?")
        await self._app_launcher.open_application(intent.target)
        return AssistantResponse(f"Abrindo {intent.target}.")


class OpenSiteCommand(AssistantCommand):
    def __init__(self, browser: BrowserGateway) -> None:
        self._browser = browser

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        if not intent.target:
            return AssistantResponse("Qual site devo abrir?")
        await self._browser.open_site(intent.target)
        return AssistantResponse(f"Abrindo o site {intent.target}.")


class GoogleSearchCommand(AssistantCommand):
    def __init__(self, browser: BrowserGateway) -> None:
        self._browser = browser

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        if not intent.target:
            return AssistantResponse("O que devo pesquisar?")
        await self._browser.google_search(intent.target)
        return AssistantResponse(f"Pesquisando por {intent.target}.")


class CurrentTimeCommand(AssistantCommand):
    def __init__(self, time_provider: TimeProvider) -> None:
        self._time_provider = time_provider

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        return AssistantResponse(f"Agora são {self._time_provider.current_time_text()}.")


class CurrentWeatherCommand(AssistantCommand):
    def __init__(self, weather_provider: WeatherProvider) -> None:
        self._weather_provider = weather_provider

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        temperature = await self._weather_provider.current_temperature_text()
        return AssistantResponse(f"A temperatura atual é {temperature}.")


class AIChatCommand(AssistantCommand):
    def __init__(self, ai_client: AIClient) -> None:
        self._ai_client = ai_client

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        return AssistantResponse(await self._ai_client.generate(intent.raw_text))


class UnknownCommand(AssistantCommand):
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        return AssistantResponse("Não entendi o comando. Pode repetir?")
