from __future__ import annotations

import logging

from zyron.application.commands.matcher import CommandMatcher
from zyron.application.commands.processor import (
    CommandProcessor,
    CommandResult,
)


logger = logging.getLogger(__name__)


class CommandRouter:

    def __init__(
        self,
        matcher: CommandMatcher,
        processor: CommandProcessor,
    ) -> None:
      
        self._matcher = matcher
        self._processor = processor

    async def route(
        self,
        user_text: str,
    ) -> CommandResult:

        normalized_text = self._normalize_text(user_text)

        if not normalized_text:
            return CommandResult(
                text="Não entendi. Digite ou fale algum comando.",
                source="validation",
                success=False,
            )

        logger.info(
            "Roteando mensagem do usuário: tamanho=%d",
            len(normalized_text),
        )

        command_match = self._matcher.match(normalized_text)

        logger.info(
            "Intenção identificada: intent=%s confidence=%.2f",
            command_match.intent.value,
            command_match.confidence,
        )

        result = await self._processor.process(
            command=command_match,
            raw_text=normalized_text,
        )

        logger.info(
            (
                "Comando processado: source=%s "
                "success=%s should_exit=%s"
            ),
            result.source,
            result.success,
            result.should_exit,
        )

        return result

    async def route_many(
        self,
        messages: list[str],
    ) -> list[CommandResult]:

        results: list[CommandResult] = []

        for message in messages:
            result = await self.route(message)

            results.append(result)

            if result.should_exit:
                break

        return results

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:

        if not isinstance(text, str):
            return ""

        return " ".join(text.strip().split())
