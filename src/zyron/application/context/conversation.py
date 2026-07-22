from __future__ import annotations

from typing import Any, Protocol


class InteractionRepository(Protocol):
    def get_recent_interactions(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        ...


class ConversationContext:
    def __init__(
        self,
        repository: InteractionRepository,
        history_limit: int = 10,
    ) -> None:
        if history_limit <= 0:
            raise ValueError(
                "O limite do histórico deve ser maior que zero."
            )

        self._repository = repository
        self._history_limit = history_limit

    @property
    def history_limit(self) -> int:
        return self._history_limit

    def get_history(self) -> list[dict[str, Any]]:
        return self._repository.get_recent_interactions(
            limit=self._history_limit,
        )

    def build_prompt_context(self) -> str:
        interactions = self.get_history()

        if not interactions:
            return "Nenhuma conversa anterior registrada."

        lines: list[str] = []

        for interaction in interactions:
            user_text = str(
                interaction.get("user_text", "")
            ).strip()

            assistant_text = str(
                interaction.get("assistant_text", "")
            ).strip()

            if user_text:
                lines.append(f"Usuário: {user_text}")

            if assistant_text:
                lines.append(f"ZYRON: {assistant_text}")

        if not lines:
            return "Nenhuma conversa anterior registrada."

        return "\n".join(lines)
