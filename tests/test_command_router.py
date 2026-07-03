from __future__ import annotations

import asyncio

from commands.command_router import CommandRouter
from commands.factory import CommandFactory
from core.models import CommandIntent, CommandType


class StubAIClient:
    async def generate(self, prompt: str) -> str:
        return f"ia: {prompt}"


class StubAppLauncher:
    def __init__(self) -> None:
        self.opened: list[str] = []

    async def open_application(self, app_name: str) -> None:
        self.opened.append(app_name)


class StubBrowser:
    def __init__(self) -> None:
        self.sites: list[str] = []
        self.searches: list[str] = []

    async def open_site(self, site: str) -> None:
        self.sites.append(site)

    async def google_search(self, query: str) -> None:
        self.searches.append(query)


class StubTimeProvider:
    def current_time_text(self) -> str:
        return "10:30"


class StubWeatherProvider:
    async def current_temperature_text(self) -> str:
        return "22 graus"


def build_router() -> tuple[CommandRouter, StubAppLauncher, StubBrowser]:
    app_launcher = StubAppLauncher()
    browser = StubBrowser()
    factory = CommandFactory(
        ai_client=StubAIClient(),
        app_launcher=app_launcher,
        browser_controller=browser,
        time_service=StubTimeProvider(),
        weather_service=StubWeatherProvider(),
    )
    return CommandRouter(factory), app_launcher, browser


def test_routes_open_application_command() -> None:
    router, app_launcher, _ = build_router()
    response = asyncio.run(router.route(CommandIntent(CommandType.OPEN_APP, "abrir aplicativo calc", "calc")))

    assert response.text == "Abrindo calc."
    assert app_launcher.opened == ["calc"]


def test_routes_weather_command() -> None:
    router, _, _ = build_router()
    response = asyncio.run(router.route(CommandIntent(CommandType.CURRENT_WEATHER, "clima")))

    assert response.text == "A temperatura atual é 22 graus."
