from __future__ import annotations

from dataclasses import dataclass

from zyron.application.assistant import ZyronAssistant
from zyron.application.permissions.permission_service import PermissionService
from zyron.config.settings import Settings
from zyron.infrastructure.ai.ollama_client import OllamaClient
from zyron.infrastructure.persistence.sqlite_repository import SQLiteRepository
from zyron.plugins.loader import PluginLoadResult, PluginLoader
from zyron.plugins.registry import PluginRegistry


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    settings: Settings
    assistant: ZyronAssistant
    permissions: PermissionService
    repository: SQLiteRepository
    plugin_registry: PluginRegistry
    plugin_load_result: PluginLoadResult


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

    permissions = PermissionService()
    repository = SQLiteRepository()

    plugin_registry = PluginRegistry()
    plugin_loader = PluginLoader(plugin_registry)

    plugin_load_result = plugin_loader.load_plugins(
        initialize=True,
        enable=False,
    )

    return ApplicationContainer(
        settings=resolved_settings,
        assistant=assistant,
        permissions=permissions,
        repository=repository,
        plugin_registry=plugin_registry,
        plugin_load_result=plugin_load_result,
    )
