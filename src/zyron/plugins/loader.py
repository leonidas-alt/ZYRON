from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from types import ModuleType

from zyron.plugins.base import Plugin
from zyron.plugins.registry import PluginRegistry


@dataclass(frozen=True, slots=True)
class PluginLoadError:
    module_name: str
    message: str


@dataclass(frozen=True, slots=True)
class PluginLoadResult:
    loaded_plugins: tuple[str, ...]
    errors: tuple[PluginLoadError, ...]


class PluginLoader:
    def __init__(
        self,
        registry: PluginRegistry,
        package: ModuleType | None = None,
    ) -> None:
        self._registry = registry
        self._package = package or importlib.import_module(
            "zyron.plugins"
        )

    def load_plugins(
        self,
        initialize: bool = True,
        enable: bool = False,
    ) -> PluginLoadResult:
        loaded_plugins: list[str] = []
        errors: list[PluginLoadError] = []

        package_path = getattr(
            self._package,
            "__path__",
            None,
        )

        if package_path is None:
            return PluginLoadResult(
                loaded_plugins=(),
                errors=(
                    PluginLoadError(
                        module_name=self._package.__name__,
                        message="O pacote de plugins não possui __path__.",
                    ),
                ),
            )

        for module_info in pkgutil.iter_modules(
            package_path,
            prefix=f"{self._package.__name__}.",
        ):
            module_name = module_info.name

            if module_name.endswith(
                (
                    ".base",
                    ".loader",
                    ".registry",
                )
            ):
                continue

            try:
                module = importlib.import_module(
                    module_name
                )

                plugin = self._find_plugin(module)

                if plugin is None:
                    continue

                self._registry.register(plugin)

                if initialize:
                    plugin.initialize()

                if enable:
                    plugin.enable()

                loaded_plugins.append(
                    plugin.name
                )

            except Exception as error:
                errors.append(
                    PluginLoadError(
                        module_name=module_name,
                        message=str(error),
                    )
                )

        return PluginLoadResult(
            loaded_plugins=tuple(
                loaded_plugins
            ),
            errors=tuple(errors),
        )

    def _find_plugin(
        self,
        module: ModuleType,
    ) -> Plugin | None:
        plugin = getattr(
            module,
            "plugin",
            None,
        )

        if isinstance(
            plugin,
            Plugin,
        ):
            return plugin

        create_plugin = getattr(
            module,
            "create_plugin",
            None,
        )

        if callable(create_plugin):
            created_plugin = create_plugin()

            if isinstance(
                created_plugin,
                Plugin,
            ):
                return created_plugin

        return None
