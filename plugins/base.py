from __future__ import annotations
from typing import Protocol
from core.models import CommandType
from core.ports import AssistantCommand


class CommandPlugin(Protocol):
    """Simple plugin contract for registering command handlers."""

    name: str

    def commands(self) -> dict[CommandType, AssistantCommand]:
        """Return command handlers provided by the plugin."""
