from __future__ import annotations
from core.models import CommandType
from core.ports import AssistantCommand
from plugins.base import CommandPlugin


class PluginManager:
    def __init__(self) -> None:
        self._plugins: list[CommandPlugin] = []

    def register(self, plugin: CommandPlugin) -> None:
        self._plugins.append(plugin)

    def command_overrides(self) -> dict[CommandType, AssistantCommand]:
        commands: dict[CommandType, AssistantCommand] = {}
        for plugin in self._plugins:
            commands.update(plugin.commands())
        return commands
