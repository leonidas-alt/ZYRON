from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("processes", "Capacidade local processes"), (skill("processes", ("processes", "status processes", "usar processes"), dangerous=True),), "Capacidade local processes preparada. Confirmação obrigatória para ações perigosas.")
