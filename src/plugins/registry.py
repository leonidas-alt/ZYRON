from __future__ import annotations
import logging
from domain.models import CommandIntent, Skill
from domain.ports import PluginInterface

logger = logging.getLogger(__name__)

class PluginRegistry:
    def __init__(self) -> None: self._plugins: dict[str, PluginInterface] = {}
    def register(self, plugin: PluginInterface) -> None:
        meta = plugin.metadata
        if not meta.name or not meta.description or not meta.version or not meta.author: raise ValueError("Plugin metadata incompleto")
        if meta.name in self._plugins: raise ValueError(f"Plugin duplicado: {meta.name}")
        self._plugins[meta.name] = plugin
    def all(self) -> tuple[PluginInterface, ...]: return tuple(self._plugins.values())
    def skills(self) -> tuple[Skill, ...]: return tuple(skill for plugin in self._plugins.values() for skill in plugin.skills())
    def find(self, intent: CommandIntent) -> PluginInterface | None:
        if intent.plugin_name: return self._plugins.get(intent.plugin_name)
        return next((plugin for plugin in self._plugins.values() if plugin.can_handle(intent)), None)
