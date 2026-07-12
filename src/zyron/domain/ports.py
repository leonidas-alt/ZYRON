from __future__ import annotations

from abc import ABC, abstractmethod


class AIClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Gera uma resposta a partir de um prompt."""