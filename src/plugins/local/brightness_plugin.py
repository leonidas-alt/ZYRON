from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("brightness", "Capacidade local brightness"), (skill("brightness", ("brightness", "status brightness", "usar brightness"), dangerous=False),), "Capacidade local brightness preparada. Comando seguro recebido: {{target}}.")
