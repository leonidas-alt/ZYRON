from __future__ import annotations

from typing import Iterator

from zyron.plugins.base import Plugin


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(
        self,
        plugin: Plugin,
    ) -> None:
        key = plugin.name.lower()

        if key in self._plugins:
            raise ValueError(
                f"O plugin '{plugin.name}' já está registrado."
            )

        self._plugins[key] = plugin

    def unregister(
        self,
        plugin_name: str,
    ) -> bool:
        key = plugin_name.lower()

        if key not in self._plugins:
            return False

        del self._plugins[key]

        return True

    def get(
        self,
        plugin_name: str,
    ) -> Plugin | None:
        return self._plugins.get(plugin_name.lower())

    def require(
        self,
        plugin_name: str,
    ) -> Plugin:
        plugin = self.get(plugin_name)

        if plugin is None:
            raise LookupError(
                f"Plugin '{plugin_name}' não encontrado."
            )

        return plugin

    def exists(
        self,
        plugin_name: str,
    ) -> bool:
        return plugin_name.lower() in self._plugins

    def enable(
        self,
        plugin_name: str,
    ) -> None:
        self.require(plugin_name).enable()

    def disable(
        self,
        plugin_name: str,
    ) -> None:
        self.require(plugin_name).disable()

    def initialize_all(self) -> None:
        for plugin in self._plugins.values():
            plugin.initialize()

    def enable_all(self) -> None:
        for plugin in self._plugins.values():
            plugin.enable()

    def disable_all(self) -> None:
        for plugin in self._plugins.values():
            plugin.disable()

    def list_plugins(self) -> list[Plugin]:
        return sorted(
            self._plugins.values(),
            key=lambda plugin: plugin.name.lower(),
        )

    def list_enabled(self) -> list[Plugin]:
        return [
            plugin
            for plugin in self.list_plugins()
            if plugin.is_enabled
        ]

    def list_disabled(self) -> list[Plugin]:
        return [
            plugin
            for plugin in self.list_plugins()
            if not plugin.is_enabled
        ]

    def health_check(self) -> dict[str, bool]:
        return {
            plugin.name: plugin.health_check()
            for plugin in self.list_plugins()
        }

    def clear(self) -> None:
        self._plugins.clear()

    def __contains__(
        self,
        plugin_name: object,
    ) -> bool:
        if not isinstance(plugin_name, str):
            return False

        return self.exists(plugin_name)

    def __len__(self) -> int:
        return len(self._plugins)

    def __iter__(self) -> Iterator[Plugin]:
        return iter(self.list_plugins())
