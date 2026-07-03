from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from core.models import CommandIntent, CommandType
from core.ports import CommandInterpreterPort

IntentParser = Callable[[str, str], CommandIntent | None]


@dataclass(frozen=True)
class PrefixRule:
    prefixes: tuple[str, ...]
    command_type: CommandType

    def parse(self, normalized: str, original: str) -> CommandIntent | None:
        for prefix in self.prefixes:
            if normalized.startswith(prefix):
                return CommandIntent(
                    command_type=self.command_type,
                    raw_text=original,
                    target=normalized.removeprefix(prefix).strip(),
                )
        return None


@dataclass(frozen=True)
class KeywordRule:
    keywords: tuple[str, ...]
    command_type: CommandType

    def parse(self, normalized: str, original: str) -> CommandIntent | None:
        if any(keyword in normalized for keyword in self.keywords):
            return CommandIntent(self.command_type, original)
        return None


class CommandInterpreter(CommandInterpreterPort):
    """Strategy-based natural-language command interpreter for Portuguese commands."""

    def __init__(self, rules: tuple[PrefixRule | KeywordRule, ...] | None = None) -> None:
        self._rules = rules or (
            PrefixRule(("abrir aplicativo ",), CommandType.OPEN_APP),
            PrefixRule(("abrir site ",), CommandType.OPEN_SITE),
            PrefixRule(("pesquisar ", "pesquise "), CommandType.GOOGLE_SEARCH),
            KeywordRule(("horas", "horário"), CommandType.CURRENT_TIME),
            KeywordRule(("temperatura", "clima"), CommandType.CURRENT_WEATHER),
        )

    def interpret(self, text: str) -> CommandIntent:
        normalized = text.lower().strip()
        if not normalized:
            return CommandIntent(CommandType.UNKNOWN, text)

        for rule in self._rules:
            intent = rule.parse(normalized, text)
            if intent is not None:
                return intent

        return CommandIntent(CommandType.AI_CHAT, text)
