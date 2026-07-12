from __future__ import annotations
import importlib, inspect, logging, pkgutil
from typing import Any
from core.config import Settings
from application.memory import MemoryService
from infrastructure.persistence import SQLiteRepository
from automation.browser_controller import BrowserController
from automation.app_launcher import AppLauncher
from services.time_service import TimeService
from services.weather_service import WeatherService
from domain.ports import PluginInterface
from plugins.registry import PluginRegistry
logger = logging.getLogger(__name__)

class PluginLoader:
    def _default_dependencies(self) -> dict[str, Any]:
        settings = Settings.from_env()
        repo = SQLiteRepository(settings.database_path)
        return {"memory_service": MemoryService(repo), "browser_controller": BrowserController(), "application_launcher": AppLauncher(), "time_provider": TimeService(), "weather_provider": WeatherService(settings.openweather_api_key, settings.openweather_city)}

    def __init__(self, package: str = "plugins", dependencies: dict[str, Any] | None = None) -> None:
        self._package = package; self._dependencies = dependencies or self._default_dependencies()
    def discover(self) -> PluginRegistry:
        registry = PluginRegistry(); package = importlib.import_module(self._package)
        for module_info in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            try:
                module = importlib.import_module(module_info.name); factory = getattr(module, "create_plugin", None)
                if not callable(factory): continue
                sig = inspect.signature(factory)
                kwargs = {name: self._dependencies[name] for name in sig.parameters if name in self._dependencies}
                if len(kwargs) != len(sig.parameters):
                    logger.warning("Plugin %s ignorado por dependências ausentes", module_info.name); continue
                plugin = factory(**kwargs)
                if isinstance(plugin, PluginInterface): registry.register(plugin)
            except Exception:
                logger.exception("Falha ao carregar plugin %s", module_info.name)
        return registry
