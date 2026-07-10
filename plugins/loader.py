from __future__ import annotations

import importlib
import inspect
import pkgutil
from collections.abc import Callable
from typing import Any

from domain.ports import PluginInterface
from plugins.dependencies import PluginDependencies
from plugins.registry import PluginRegistry


class PluginLoader:
    """Discovers plugin modules and instantiates their create_plugin factories."""

    def __init__(
        self,
        package: str = "plugins",
        dependencies: PluginDependencies | None = None,
    ) -> None:
        self._package = package
        self._dependencies = dependencies or PluginDependencies()

    def discover(self) -> PluginRegistry:
        registry = PluginRegistry()
        package = importlib.import_module(self._package)
        for module_info in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            module = importlib.import_module(module_info.name)
            factory = getattr(module, "create_plugin", None)
            if callable(factory):
                registry.register(self._create(factory))
        return registry

    def _create(self, factory: Callable[..., PluginInterface]) -> PluginInterface:
        parameters = inspect.signature(factory).parameters
        if "dependencies" in parameters:
            plugin = factory(dependencies=self._dependencies)
        else:
            plugin = factory()
        if not isinstance(plugin, PluginInterface):
            raise TypeError(f"Invalid plugin factory result: {factory!r}")
        return plugin
