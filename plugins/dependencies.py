from __future__ import annotations

from dataclasses import dataclass

from application.memory import MemoryService


@dataclass(frozen=True)
class PluginDependencies:
    """Runtime services optionally consumed by auto-discovered plugins."""

    memory: MemoryService | None = None
