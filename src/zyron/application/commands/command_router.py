from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from zyron.application.commands.command_result import CommandResult


class CommandHandler(Protocol):
    def handle(
        self,
        command: str,
    ) -> CommandResult:
        ...


class CommandRouter:
    def __init__(
        self,
        handlers: Iterable[CommandHandler],
    ) -> None:
        self._handlers = tuple(handlers)

    def route(
        self,
        command: str,
    ) -> CommandResult:
        normalized_command = command.strip()

        if not normalized_command:
            return CommandResult.not_handled()

        for handler in self._handlers:
            result = handler.handle(
                normalized_command
            )

            if result.handled:
                return result

        return CommandResult.not_handled()