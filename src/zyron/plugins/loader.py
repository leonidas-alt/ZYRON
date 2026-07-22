from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass, field
from types import ModuleType
from typing import Iterable

import zyron.plugins
from zyron.plugins.base import Plugin
from zyron.plugins.registry import PluginRegistry


@dataclass(frozen=True, slots=True)
class PluginLoadError:
    module_name: str
    plugin_name: str | None
    message: str


@dataclass(slots=True)
class PluginLoadResult:
    loaded: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[PluginLoadError] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors

    @property
    def loaded_count(self) -> int:
        return len(self.loaded)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)

    @property
    def error_count(self) -> int:
        return len(self.errors)


class PluginLoader:
    IGNORED_MODULES = {
        "zyron.plugins.base",
        "zyron.plugins.loader",
        "zyron.plugins.registry",
    }

    def __init__(
        self,
        registry: PluginRegistry,
        package: ModuleType = zyron.plugins,
    ) -> None:
        self._registry = registry
        self._package = package

    def load_plugins(
        self,
        initialize: bool = True,
        enable: bool = False,
    ) -> PluginLoadResult:
        result = PluginLoadResult()

        for module_name in self.discover_modules():
            try:
                module = importlib.import_module(module_name)
            except Exception as error:
                result.errors.append(
                    PluginLoadError(
                        module_name=module_name,
                        plugin_name=None,
                        message=str(error),
                    )
                )
                continue

            plugin_classes = self.find_plugin_classes(module)

            if not plugin_classes:
                result.skipped.append(module_name)
                continue

            for plugin_class in plugin_classes:
                self._load_plugin_class(
                    module_name=module_name,
                    plugin_class=plugin_class,
                    result=result,
                    initialize=initialize,
                    enable=enable,
                )

        return result

    def load_module(
        self,
        module_name: str,
        initialize: bool = True,
        enable: bool = False,
    ) -> PluginLoadResult:
        result = PluginLoadResult()

        try:
            module = importlib.import_module(module_name)
        except Exception as error:
            result.errors.append(
                PluginLoadError(
                    module_name=module_name,
                    plugin_name=None,
                    message=str(error),
                )
            )
            return result

        plugin_classes = self.find_plugin_classes(module)

        if not plugin_classes:
            result.skipped.append(module_name)
            return result

        for plugin_class in plugin_classes:
            self._load_plugin_class(
                module_name=module_name,
                plugin_class=plugin_class,
                result=result,
                initialize=initialize,
                enable=enable,
            )

        return result

    def discover_modules(self) -> list[str]:
        package_path = getattr(self._package, "__path__", None)

        if package_path is None:
            return []

        prefix = f"{self._package.__name__}."

        modules = [
            module_info.name
            for module_info in pkgutil.walk_packages(
                package_path,
                prefix=prefix,
            )
            if not module_info.ispkg
            and module_info.name not in self.IGNORED_MODULES
        ]

        return sorted(modules)

    def find_plugin_classes(
        self,
        module: ModuleType,
    ) -> list[type[Plugin]]:
        classes: list[type[Plugin]] = []

        for _, candidate in inspect.getmembers(
            module,
            inspect.isclass,
        ):
            if candidate is Plugin:
                continue

            if not issubclass(candidate, Plugin):
                continue

            if candidate.__module__ != module.__name__:
                continue

            if inspect.isabstract(candidate):
                continue

            classes.append(candidate)

        return classes

    def register_instances(
        self,
        plugins: Iterable[Plugin],
        initialize: bool = True,
        enable: bool = False,
    ) -> PluginLoadResult:
        result = PluginLoadResult()

        for plugin in plugins:
            plugin_name = plugin.name

            try:
                self._register_plugin(
                    plugin=plugin,
                    initialize=initialize,
                    enable=enable,
                )
                result.loaded.append(plugin_name)
            except ValueError:
                result.skipped.append(plugin_name)
            except Exception as error:
                result.errors.append(
                    PluginLoadError(
                        module_name=plugin.__class__.__module__,
                        plugin_name=plugin_name,
                        message=str(error),
                    )
                )

        return result

    def _load_plugin_class(
        self,
        module_name: str,
        plugin_class: type[Plugin],
        result: PluginLoadResult,
        initialize: bool,
        enable: bool,
    ) -> None:
        plugin_name = plugin_class.__name__

        if not self._can_instantiate(plugin_class):
            result.skipped.append(
                f"{module_name}.{plugin_name}"
            )
            return

        try:
            plugin = plugin_class()
            self._register_plugin(
                plugin=plugin,
                initialize=initialize,
                enable=enable,
            )
            result.loaded.append(plugin.name)
        except ValueError:
            result.skipped.append(plugin_name)
        except Exception as error:
            result.errors.append(
                PluginLoadError(
                    module_name=module_name,
                    plugin_name=plugin_name,
                    message=str(error),
                )
            )

    def _register_plugin(
        self,
        plugin: Plugin,
        initialize: bool,
        enable: bool,
    ) -> None:
        self._registry.register(plugin)

        if initialize:
            plugin.initialize()

        if enable:
            plugin.enable()

    @staticmethod
    def _can_instantiate(
        plugin_class: type[Plugin],
    ) -> bool:
        signature = inspect.signature(plugin_class)

        return all(
            parameter.default is not inspect.Parameter.empty
            or parameter.kind
            in {
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            }
            for parameter in signature.parameters.values()
        )
