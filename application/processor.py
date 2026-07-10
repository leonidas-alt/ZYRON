from __future__ import annotations

from typing import Protocol

from application.context import ContextService
from application.events import EventBus
from application.memory import MemoryService
from application.skills import IntentMatcher
from domain.models import AssistantResponse, CommandIntent


class IntentRouter(Protocol):
    async def route(self, intent: CommandIntent) -> AssistantResponse: ...


class CommandProcessor:
    def __init__(
        self,
        matcher: IntentMatcher,
        router: IntentRouter,
        context: ContextService,
        memory: MemoryService,
        events: EventBus,
    ) -> None:
        self._matcher = matcher
        self._router = router
        self._context = context
        self._memory = memory
        self._events = events

    async def process(self, text: str) -> str:
        await self._events.publish("command.received", {"text": text})
        intent = self._build_contextual_intent(text)
        response = await self._router.route(intent)
        await self._record_interaction(text, response, intent)
        await self._events.publish(
            "command.completed",
            {"text": text, "response": response.text},
        )
        return response.text

    def _build_contextual_intent(self, text: str) -> CommandIntent:
        intent = self._matcher.match(text)
        return CommandIntent(
            command_type=intent.command_type,
            raw_text=intent.raw_text,
            target=intent.target,
            confidence=intent.confidence,
            skill_name=intent.skill_name,
            plugin_name=intent.plugin_name,
            metadata=self._context.enrich(intent.metadata),
        )

    async def _record_interaction(
        self,
        text: str,
        response: AssistantResponse,
        intent: CommandIntent,
    ) -> None:
        await self._memory.save_interaction(text, response.text)
        self._context.update(
            text,
            response.text,
            intent.plugin_name,
            intent.target or str(intent.metadata.get("active_subject") or ""),
        )
