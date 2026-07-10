from __future__ import annotations

from domain.models import CommandIntent, Skill
from domain.ports import PluginInterface


class PluginRegistry:
    """In-memory catalog of plugins and their exposed skills."""

    def __init__(self) -> None:
        self._plugins: dict[str, PluginInterface] = {}
        self._skill_to_plugin: dict[str, str] = {}

    def register(self, plugin: PluginInterface) -> None:
        self._plugins[plugin.metadata.name] = plugin
        for skill in plugin.skills():
            self._skill_to_plugin[skill.name] = plugin.metadata.name

    def all(self) -> tuple[PluginInterface, ...]:
        return tuple(self._plugins.values())

    def skills(self) -> tuple[Skill, ...]:
        return tuple(skill for plugin in self._plugins.values() for skill in plugin.skills())

    def find(self, intent: CommandIntent) -> PluginInterface | None:
        plugin_name = intent.plugin_name or self._skill_to_plugin.get(intent.skill_name or "")
        if plugin_name:
            return self._plugins.get(plugin_name)
        for plugin in self._plugins.values():
            if plugin.can_handle(intent):
                return plugin
        return None
