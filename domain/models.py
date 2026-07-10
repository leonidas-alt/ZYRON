from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

class CommandType(str, Enum):
    OPEN_APP="open_app"; OPEN_SITE="open_site"; GOOGLE_SEARCH="google_search"; CURRENT_TIME="current_time"; CURRENT_WEATHER="current_weather"; AI_CHAT="ai_chat"; MEMORY="memory"; SYSTEM="system"; UNKNOWN="unknown"

@dataclass(frozen=True)
class CommandIntent:
    command_type: CommandType
    raw_text: str
    target: str | None = None
    confidence: float = 0.0
    skill_name: str | None = None
    plugin_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class AssistantResponse:
    text: str
    spoken: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass(frozen=True)
class Interaction:
    user_text: str
    assistant_text: str
    created_at: datetime

@dataclass(frozen=True)
class MemoryItem:
    key: str
    value: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass(frozen=True)
class Capability:
    name: str
    description: str
    dangerous: bool = False
    requires_credentials: bool = False

@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    examples: tuple[str, ...]
    keywords: tuple[str, ...]
    synonyms: tuple[str, ...] = ()
    capability: Capability | None = None

@dataclass(frozen=True)
class PluginMetadata:
    name: str
    description: str
    version: str = "0.1.0"
    author: str = "ZYRON"
