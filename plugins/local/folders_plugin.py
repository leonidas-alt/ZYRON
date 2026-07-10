from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("folders", "Capacidade local folders"), (skill("folders", ("folders", "status folders", "usar folders"), dangerous=True),), "Capacidade local folders preparada. Confirmação obrigatória para ações perigosas.")
