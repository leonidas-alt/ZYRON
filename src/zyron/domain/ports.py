from __future__ import annotations

from abc import ABC, abstractmethod


class AIClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError
