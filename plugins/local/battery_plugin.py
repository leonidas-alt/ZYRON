from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("battery", "Capacidade local battery"), (skill("battery", ("battery", "status battery", "usar battery"), dangerous=False),), "Capacidade local battery preparada. Comando seguro recebido: {{target}}.")
