from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from domain.models import Interaction

_REFERENCE_WORDS = {"nele", "nela", "nisso", "lá", "la", "ali", "esse", "essa", "isso", "mesmo"}


@dataclass
class ConversationContext:
    last_command: str | None = None
    last_type: str | None = None
    last_plugin: str | None = None
    last_skill: str | None = None
    last_target: str | None = None
    last_application: str | None = None
    last_site: str | None = None
    last_search: str | None = None
    last_memory_accessed: str | None = None
    last_response: str | None = None
    active_subject: str | None = None
    interaction_count: int = 0
    pending_action: str | None = None
    last_time: datetime | None = None
    last_conversation: str | None = None
    last_intent: str | None = None
    recent: list[Interaction] = field(default_factory=list)

    def update(self, user_text: str | None = None, assistant_text: str | None = None, plugin_name: str | None = None,
               target: str | None = None, skill_name: str | None = None, command_type: str | None = None,
               metadata: dict[str, Any] | None = None) -> None:
        metadata = metadata or {}
        if user_text:
            self.last_command = user_text
            self.last_intent = user_text
            self.last_conversation = user_text
        if assistant_text is not None:
            self.last_response = assistant_text
        self.last_plugin = plugin_name or self.last_plugin
        self.last_skill = skill_name or self.last_skill
        self.last_type = command_type or self.last_type
        if target:
            self.last_target = target
            self.active_subject = target
        elif plugin_name:
            self.active_subject = self.active_subject or plugin_name
        site = metadata.get("site") or metadata.get("url")
        app = metadata.get("application")
        search = metadata.get("search") or metadata.get("query")
        memory = metadata.get("memory_key")
        if isinstance(site, str):
            self.last_site = site; self.active_subject = site
        if isinstance(app, str):
            self.last_application = app; self.active_subject = app
        if isinstance(search, str): self.last_search = search
        if isinstance(memory, str): self.last_memory_accessed = memory
        self.interaction_count += 1
        self.last_time = datetime.now(UTC)

    def clear(self) -> None:
        self.active_subject = None; self.pending_action = None

    def reset(self) -> None:
        self.__dict__.update(ConversationContext().__dict__)

    def to_metadata(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if k != "recent" and v is not None}

    def resolve_reference(self, text: str) -> str | None:
        words = {w.strip(',.!?;:').lower() for w in text.split()}
        if not words & _REFERENCE_WORDS:
            return None
        return self.last_site or self.last_application or self.last_target or self.active_subject

    def as_prompt(self) -> str:
        lines = [f"Assunto ativo: {self.active_subject}"] if self.active_subject else []
        for item in self.recent:
            lines.append(f"Usuário: {item.user_text}\nZYRON: {item.assistant_text}")
        return "\n".join(lines)


class ContextService:
    def __init__(self, context: ConversationContext | None = None) -> None:
        self.context = context or ConversationContext()
    def enrich(self, metadata: dict[str, object]) -> dict[str, object]:
        return {**metadata, **self.context.to_metadata(), "conversation_context": self.context.as_prompt(), "active_subject": self.context.active_subject}
    def resolve_reference(self, text: str) -> str | None:
        return self.context.resolve_reference(text)
    def update(self, user_text: str, assistant_text: str, plugin_name: str | None, target: str | None, skill_name: str | None = None, command_type: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        self.context.update(user_text, assistant_text, plugin_name, target, skill_name, command_type, metadata)
