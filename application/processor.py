from __future__ import annotations
from application.context import ContextService
from application.events import EventBus
from application.memory import MemoryService
from application.router import CommandRouter
from application.skills import IntentMatcher

class CommandProcessor:
    def __init__(self, matcher: IntentMatcher, router: CommandRouter, context: ContextService, memory: MemoryService, events: EventBus) -> None:
        self._matcher=matcher; self._router=router; self._context=context; self._memory=memory; self._events=events
    async def process(self, text: str) -> str:
        await self._events.publish("command.received", {"text": text})
        intent = self._matcher.match(text)
        intent = type(intent)(intent.command_type, intent.raw_text, intent.target, intent.confidence, intent.skill_name, intent.plugin_name, self._context.enrich(intent.metadata))
        response = await self._router.route(intent)
        await self._memory._repo.save_interaction(text, response.text)  # repository owns history + persistent memory
        self._context.update(text, response.text, intent.plugin_name, intent.target or str(intent.metadata.get("active_subject") or ""))
        await self._events.publish("command.completed", {"text": text, "response": response.text})
        return response.text
