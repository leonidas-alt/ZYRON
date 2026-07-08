from __future__ import annotations
from core.models import Interaction


class ConversationMemory:
    """Builds a compact conversational context from saved interactions."""

    def __init__(self, max_interactions: int = 5) -> None:
        self.max_interactions = max_interactions

    def format(self, interactions: list[Interaction]) -> str:
        if not interactions:
            return ""

        recent = interactions[-self.max_interactions :]
        lines: list[str] = []
        for interaction in recent:
            lines.append(f"Usuário: {interaction.user_text}")
            lines.append(f"ZYRON: {interaction.assistant_text}")
        return "\n".join(lines)
