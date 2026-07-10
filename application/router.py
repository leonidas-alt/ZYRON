from __future__ import annotations
from domain.models import AssistantResponse, CommandIntent
from plugins.registry import PluginRegistry

class CommandRouter:
    def __init__(self, registry: PluginRegistry) -> None: self._registry = registry
    async def route(self, intent: CommandIntent) -> AssistantResponse:
        plugin = self._registry.find(intent)
        if plugin is None:
            return AssistantResponse("Não encontrei um plugin capaz de executar esse comando.")
        return await plugin.execute(intent)
