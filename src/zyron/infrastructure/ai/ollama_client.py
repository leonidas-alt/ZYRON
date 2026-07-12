from __future__ import annotations

import asyncio
from typing import Any

import requests

from zyron.domain.exceptions import AIResponseError, AIUnavailableError
from zyron.domain.ports import AIClient


class OllamaClient(AIClient):
    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 60,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    async def generate(self, prompt: str) -> str:
        if not prompt.strip():
            return ""

        return await asyncio.to_thread(self._generate_sync, prompt)

    def _generate_sync(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise AIUnavailableError(
                "Não consegui acessar o Ollama. "
                "Verifique se ele está instalado e em execução."
            ) from exc

        try:
            payload: dict[str, Any] = response.json()
        except ValueError as exc:
            raise AIResponseError(
                "O Ollama retornou uma resposta que não é JSON."
            ) from exc

        generated_text = str(payload.get("response", "")).strip()

        if not generated_text:
            raise AIResponseError(
                "O Ollama não retornou conteúdo."
            )

        return generated_text