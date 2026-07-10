from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("apps", "Capacidade local apps"), (skill("apps", ("apps", "status apps", "usar apps"), dangerous=True),), "Capacidade local apps preparada. Confirmação obrigatória para ações perigosas.")
