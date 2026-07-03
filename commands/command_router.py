from __future__ import annotations

from commands.factory import CommandFactory
from core.models import AssistantResponse, CommandIntent


class CommandRouter:
    """Routes intents to command handlers using Strategy + Command patterns."""

    def __init__(self, command_factory: CommandFactory) -> None:
        self._command_factory = command_factory

    async def route(self, intent: CommandIntent) -> AssistantResponse:
        command = self._command_factory.get(intent.command_type)
        return await command.execute(intent)
