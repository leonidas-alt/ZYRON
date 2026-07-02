from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CommandType(str, Enum):

    OPEN_APP = "open_app"
    OPEN_SITE = "open_site"
    GOOGLE_SEARCH = "google_search"
    CURRENT_TIME = "current_time"
    CURRENT_WEATHER = "current_weather"
    AI_CHAT = "ai_chat"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CommandIntent:

    command_type: CommandType
    raw_text: str
    target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssistantResponse:

    text: str
    spoken: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
