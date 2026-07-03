from __future__ import annotations

import asyncio
from typing import Any

import requests

from core.ports import AIClient


class OllamaClient(AIClient):
    """Async adapter for the local Ollama HTTP API."""

    def __init__(self, base_url: str, model: str, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def generate(self, prompt: str) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return str(data.get("response", "")).strip()
        except requests.Timeout:
            return "O modelo local demorou para responder. Tente novamente em instantes."
        except requests.ConnectionError:
            return "Não consegui conectar ao Ollama local. Verifique se o serviço está ativo."
        except requests.HTTPError as exc:
            return f"O Ollama retornou uma falha HTTP: {exc.response.status_code}."
        except requests.JSONDecodeError:
            return "Recebi uma resposta inválida do Ollama local."
