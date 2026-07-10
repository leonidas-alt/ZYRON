from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("files", "Capacidade local files"), (skill("files", ("files", "status files", "usar files"), dangerous=True),), "Capacidade local files preparada. Confirmação obrigatória para ações perigosas.")
