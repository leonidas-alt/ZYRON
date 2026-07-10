from __future__ import annotations
from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]
class EventBus:
    def __init__(self) -> None: self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
    def subscribe(self, event: str, handler: EventHandler) -> None: self._handlers[event].append(handler)
    async def publish(self, event: str, payload: dict[str, Any]) -> None:
        for handler in self._handlers[event]: await handler(payload)
