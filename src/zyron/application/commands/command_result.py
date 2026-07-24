from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CommandResult:
    handled: bool
    message: str
    data: Any | None = None

    @classmethod
    def success(
        cls,
        message: str,
        data: Any | None = None,
    ) -> "CommandResult":
        return cls(
            handled=True,
            message=message.strip(),
            data=data,
        )

    @classmethod
    def not_handled(cls) -> "CommandResult":
        return cls(
            handled=False,
            message="",
            data=None,
        )

    @classmethod
    def failure(
        cls,
        message: str,
        data: Any | None = None,
    ) -> "CommandResult":
        return cls(
            handled=True,
            message=message.strip(),
            data=data,
        )