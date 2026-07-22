from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re


class Intent(StrEnum):

    CHAT = "chat"

    OPEN_APPLICATION = "open_application"

    SAVE_MEMORY = "save_memory"

    RECALL_MEMORY = "recall_memory"

    DELETE_MEMORY = "delete_memory"

    LIST_MEMORIES = "list_memories"

    GET_TIME = "get_time"

    EXIT = "exit"

    UNKNOWN = "unknown"


@dataclass(slots=True)
class CommandMatch:

    intent: Intent

    payload: dict[str, str]

    confidence: float


class CommandMatcher:

    EXIT_COMMANDS = {
        "sair",
        "fechar",
        "encerrar",
        "quit",
        "exit",
    }

    TIME_PATTERNS = (
        "que horas são",
        "horas",
        "hora",
    )

    LIST_PATTERNS = (
        "liste memórias",
        "listar memórias",
        "mostrar memórias",
        "minhas memórias",
    )

    OPEN_PATTERN = re.compile(
        r"^(abra|abrir)\s+(?P<application>.+)$",
        re.IGNORECASE,
    )

    REMEMBER_PATTERN = re.compile(
        r"^lembre\s+que\s+(?P<key>.+?)\s+é\s+(?P<value>.+)$",
        re.IGNORECASE,
    )

    RECALL_PATTERN = re.compile(
        r"^(qual\s+é|qual\s+o|qual\s+a)\s+(?P<key>.+)\??$",
        re.IGNORECASE,
    )

    DELETE_PATTERN = re.compile(
        r"^(esqueça|apague)\s+(?P<key>.+)$",
        re.IGNORECASE,
    )

    def match(self, text: str) -> CommandMatch:

        cleaned = text.strip().lower()

        if not cleaned:
            return CommandMatch(
                intent=Intent.UNKNOWN,
                payload={},
                confidence=0.0,
            )

        if cleaned in self.EXIT_COMMANDS:
            return CommandMatch(
                intent=Intent.EXIT,
                payload={},
                confidence=1.0,
            )

        if cleaned in self.TIME_PATTERNS:
            return CommandMatch(
                intent=Intent.GET_TIME,
                payload={},
                confidence=1.0,
            )

        if cleaned in self.LIST_PATTERNS:
            return CommandMatch(
                intent=Intent.LIST_MEMORIES,
                payload={},
                confidence=1.0,
            )

        remember = self.REMEMBER_PATTERN.match(cleaned)

        if remember:
            return CommandMatch(
                intent=Intent.SAVE_MEMORY,
                payload={
                    "key": remember.group("key"),
                    "value": remember.group("value"),
                },
                confidence=0.95,
            )

        recall = self.RECALL_PATTERN.match(cleaned)

        if recall:
            return CommandMatch(
                intent=Intent.RECALL_MEMORY,
                payload={
                    "key": recall.group("key"),
                },
                confidence=0.90,
            )

        delete = self.DELETE_PATTERN.match(cleaned)

        if delete:
            return CommandMatch(
                intent=Intent.DELETE_MEMORY,
                payload={
                    "key": delete.group("key"),
                },
                confidence=0.95,
            )

        open_application = self.OPEN_PATTERN.match(cleaned)

        if open_application:
            return CommandMatch(
                intent=Intent.OPEN_APPLICATION,
                payload={
                    "application": open_application.group(
                        "application"
                    )
                },
                confidence=0.95,
            )

        return CommandMatch(
            intent=Intent.CHAT,
            payload={
                "prompt": text,
            },
            confidence=0.70,
        )
