from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("network", "Capacidade local network"), (skill("network", ("network", "status network", "usar network"), dangerous=False),), "Capacidade local network preparada. Comando seguro recebido: {{target}}.")
