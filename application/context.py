from __future__ import annotations

from dataclasses import dataclass, field

from domain.models import Interaction


@dataclass
class ConversationContext:
    """Short-term conversation state shared across a command pipeline run."""

    active_subject: str | None = None
    last_intent: str | None = None
    recent: list[Interaction] = field(default_factory=list)

    def update(
        self,
        user_text: str,
        assistant_text: str,
        plugin_name: str | None = None,
        target: str | None = None,
    ) -> None:
        """Update the context from the latest interaction."""

        subject = target or plugin_name
        if subject:
            self.active_subject = subject
        self.last_intent = user_text

    def as_prompt(self) -> str:
        """Return a compact prompt fragment suitable for AI fallback adapters."""

        lines = [f"Assunto ativo: {self.active_subject}"] if self.active_subject else []
        for item in self.recent:
            lines.append(f"Usuário: {item.user_text}\nZYRON: {item.assistant_text}")
        return "\n".join(lines)


class ContextService:
    """Coordinates short-term context enrichment and updates."""

    def __init__(self, context: ConversationContext | None = None) -> None:
        self.context = context or ConversationContext()

    def load_recent(self, interactions: list[Interaction]) -> None:
        self.context.recent = interactions

    def enrich(self, metadata: dict[str, object]) -> dict[str, object]:
        return {
            **metadata,
            "conversation_context": self.context.as_prompt(),
            "active_subject": self.context.active_subject,
        }

    def update(
        self,
        user_text: str,
        assistant_text: str,
        plugin_name: str | None,
        target: str | None,
    ) -> None:
        self.context.update(user_text, assistant_text, plugin_name, target)
