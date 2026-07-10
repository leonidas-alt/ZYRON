from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("cpu", "Capacidade local cpu"), (skill("cpu", ("cpu", "status cpu", "usar cpu"), dangerous=False),), "Capacidade local cpu preparada. Comando seguro recebido: {{target}}.")
