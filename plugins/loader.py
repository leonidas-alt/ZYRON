from __future__ import annotations
import importlib, pkgutil
from domain.ports import PluginInterface
from plugins.registry import PluginRegistry

class PluginLoader:
    def __init__(self, package: str = "plugins") -> None: self._package = package
    def discover(self) -> PluginRegistry:
        registry = PluginRegistry(); package = importlib.import_module(self._package)
        for module_info in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            module = importlib.import_module(module_info.name)
            factory = getattr(module, "create_plugin", None)
            if callable(factory):
                plugin = factory()
                if isinstance(plugin, PluginInterface): registry.register(plugin)
        return registry
