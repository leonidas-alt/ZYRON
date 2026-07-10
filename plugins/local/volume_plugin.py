from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("volume", "Capacidade local volume"), (skill("volume", ("volume", "status volume", "usar volume"), dangerous=False),), "Capacidade local volume preparada. Comando seguro recebido: {{target}}.")
