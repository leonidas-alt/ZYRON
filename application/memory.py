from __future__ import annotations

import re
from domain.models import MemoryItem
from domain.ports import MemoryRepository

class MemoryService:
    def __init__(self, repository: MemoryRepository) -> None:
        self._repository = repository

    async def save_interaction(self, user_text: str, assistant_text: str) -> None:
        await self._repository.save_interaction(user_text, assistant_text)

    def parse_memory(self, text: str) -> tuple[str, str] | None:
        raw = " ".join(text.strip().split())
        low = raw.lower()
        patterns = [
            (r"^(?:lembre que|lembrar que) meu (.+?) (?:é|eh) (.+)$", lambda m: (m.group(1), m.group(2))),
            (r"^meu nome (?:é|eh) (.+)$", lambda m: ("nome", m.group(1))),
            (r"^eu estudo (.+)$", lambda m: ("curso", m.group(1))),
            (r"^(?:lembre que|lembrar que) gosto de (.+)$", lambda m: ("preferência", f"gosto de {m.group(1)}")),
            (r"^(?:lembre que|lembrar que) (.+?) (?:é|eh) (.+)$", lambda m: (m.group(1), m.group(2))),
        ]
        for pat, fn in patterns:
            m = re.match(pat, low, flags=re.IGNORECASE)
            if m:
                key, value = fn(m)
                return key.strip(), value.strip()
        if "=" in raw:
            key, value = raw.split("=", 1); return key.strip(), value.strip()
        return None

    async def remember(self, key: str, value: str | None = None) -> tuple[str, str]:
        if value is None:
            parsed = self.parse_memory(key)
            if parsed: key, value = parsed
            else: key, value = "nota", key
        await self._repository.remember(key, value)
        return key, value

    async def recall(self, key: str) -> MemoryItem | None: return await self._repository.recall(key)
    async def list_memories(self) -> list[MemoryItem]: return await self._repository.list_memories()
    async def forget(self, key: str) -> bool: return await self._repository.forget(key)
