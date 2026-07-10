from __future__ import annotations

from application.context import ContextService
from application.events import EventBus
from application.memory import MemoryService
from application.router import CommandRouter
from application.skills import IntentMatcher
from domain.models import CommandIntent


class CommandProcessor:
    """Runs the complete command pipeline for every user input."""

    def __init__(
        self,
        matcher: IntentMatcher,
        router: CommandRouter,
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
        intent = self._with_context(self._matcher.match(text))
        response = await self._router.route(intent)
        await self._memory.save_interaction(text, response.text)
        self._context.update(text, response.text, intent.plugin_name, intent.target)
        await self._events.publish(
            "command.completed",
            {"text": text, "response": response.text},
        )
        return response.text

    def _with_context(self, intent: CommandIntent) -> CommandIntent:
        return CommandIntent(
            command_type=intent.command_type,
            raw_text=intent.raw_text,
            target=intent.target,
            confidence=intent.confidence,
            skill_name=intent.skill_name,
            plugin_name=intent.plugin_name,
            metadata=self._context.enrich(intent.metadata),
        )
