from __future__ import annotations
from domain.models import CommandIntent, Skill
from domain.ports import PluginInterface

class PluginRegistry:
    def __init__(self) -> None: self._plugins: dict[str, PluginInterface] = {}
    def register(self, plugin: PluginInterface) -> None: self._plugins[plugin.metadata.name] = plugin
    def all(self) -> tuple[PluginInterface, ...]: return tuple(self._plugins.values())
    def skills(self) -> tuple[Skill, ...]:
        return tuple(skill for plugin in self._plugins.values() for skill in plugin.skills())
    def find(self, intent: CommandIntent) -> PluginInterface | None:
        if intent.plugin_name and intent.plugin_name in self._plugins: return self._plugins[intent.plugin_name]
        for plugin in self._plugins.values():
            if plugin.can_handle(intent): return plugin
        return None
