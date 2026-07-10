from __future__ import annotations
import platform, time
from datetime import datetime
from core.ports import TimeProvider, WeatherProvider
from domain.models import AssistantResponse, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface

_STARTED = time.monotonic()
class SystemPlugin(PluginInterface):
    metadata=PluginMetadata("system", "Informações de sistema", capabilities=("system_info",), dependencies=("time_provider", "weather_provider"))
    def __init__(self, time_provider: TimeProvider, weather_provider: WeatherProvider) -> None: self._time=time_provider; self._weather=weather_provider
    def skills(self): return (Skill("system", "hora data uptime clima", ("que horas", "data de hoje", "uptime", "clima"), ("hora", "data", "uptime", "clima", "tempo")),)
    def can_handle(self, intent: CommandIntent) -> bool: return intent.skill_name == "system"
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        t=intent.raw_text.lower()
        if "clima" in t or "tempo" in t: return AssistantResponse(f"Clima: {await self._weather.current_temperature_text()}.")
        if "data" in t: return AssistantResponse(f"Hoje é {datetime.now().strftime('%d/%m/%Y')}.")
        if "uptime" in t: return AssistantResponse(f"Uptime do ZYRON: {int(time.monotonic()-_STARTED)} segundos em {platform.system()}.")
        return AssistantResponse(f"Agora são {self._time.current_time_text()}.")
def create_plugin(time_provider: TimeProvider, weather_provider: WeatherProvider) -> PluginInterface: return SystemPlugin(time_provider, weather_provider)
