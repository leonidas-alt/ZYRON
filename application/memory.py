from __future__ import annotations

from domain.models import MemoryItem
from domain.ports import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository) -> None:
        self._repository = repository

    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        await self._repository.save_interaction(user_text, assistant_text)

    async def remember(self, key: str, value: str) -> None:
        await self._repository.remember(key, value)

    async def recall(self, key: str) -> MemoryItem | None:
        return await self._repository.recall(key)

    async def list_memories(self) -> list[MemoryItem]:
        return await self._repository.list_memories()

    async def forget(self, key: str) -> bool:
        return await self._repository.forget(key)
