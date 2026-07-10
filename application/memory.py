from __future__ import annotations
from domain.models import MemoryItem
from domain.ports import MemoryRepository

class MemoryService:
    def __init__(self, repository: MemoryRepository) -> None: self._repo = repository
    async def remember(self, key: str, value: str) -> None: await self._repo.remember(key, value)
    async def recall(self, key: str) -> MemoryItem | None: return await self._repo.recall(key)
    async def list_memories(self) -> list[MemoryItem]: return await self._repo.list_memories()
    async def forget(self, key: str) -> bool: return await self._repo.forget(key)
