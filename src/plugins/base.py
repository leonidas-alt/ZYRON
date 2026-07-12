from __future__ import annotations
from typing import Protocol
from core.models import CommandType
from core.ports import AssistantCommand

class CommandPlugin(Protocol):
    name: str
    def commands(self) -> dict[CommandType, AssistantCommand]:
        ...
