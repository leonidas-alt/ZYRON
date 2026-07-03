from __future__ import annotations

from core.models import CommandType
from core.ports import (
    AIClient,
    ApplicationLauncher,
    AssistantCommand,
    BrowserGateway,
    TimeProvider,
    WeatherProvider,
)
from commands.handlers import (
    AIChatCommand,
    CurrentTimeCommand,
    CurrentWeatherCommand,
    GoogleSearchCommand,
    OpenApplicationCommand,
    OpenSiteCommand,
    UnknownCommand,
)


class CommandFactory:
    """Factory that wires command handlers without exposing concrete routing details."""

    def __init__(
        self,
        ai_client: AIClient,
        app_launcher: ApplicationLauncher,
        browser_controller: BrowserGateway,
        time_service: TimeProvider,
        weather_service: WeatherProvider,
    ) -> None:
        self._commands: dict[CommandType, AssistantCommand] = {
            CommandType.OPEN_APP: OpenApplicationCommand(app_launcher),
            CommandType.OPEN_SITE: OpenSiteCommand(browser_controller),
            CommandType.GOOGLE_SEARCH: GoogleSearchCommand(browser_controller),
            CommandType.CURRENT_TIME: CurrentTimeCommand(time_service),
            CommandType.CURRENT_WEATHER: CurrentWeatherCommand(weather_service),
            CommandType.AI_CHAT: AIChatCommand(ai_client),
            CommandType.UNKNOWN: UnknownCommand(),
        }

    def get(self, command_type: CommandType) -> AssistantCommand:
        return self._commands.get(command_type, self._commands[CommandType.UNKNOWN])
