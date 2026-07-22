from __future__ import annotations

from dataclasses import dataclass

from zyron.application.assistant import ZyronAssistant
from zyron.config.settings import Settings
from zyron.infrastructure.ai.ollama_client import OllamaClient

@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    settings: Settings
    assistant: ZyronAssistant

def build_container(
    settings: Settings | None = None,
) -> ApplicationContainer:
    resolved_settings = settings or Settings.from_env()

    ai_client = OllamaClient(
        base_url=resolved_settings.ollama_base_url,
        model=resolved_settings.ollama_model,
        timeout_seconds=resolved_settings.ollama_timeout_seconds,
    )

    assistant = ZyronAssistant(
        ai_client=ai_client,
        assistant_name=resolved_settings.assistant_name,
        owner_name=resolved_settings.owner_name,
    )

    return ApplicationContainer(
        settings=resolved_settings,
        assistant=assistant,
    )
