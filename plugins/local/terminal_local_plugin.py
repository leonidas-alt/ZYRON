from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("terminal_local", "Capacidade local terminal_local"), (skill("terminal_local", ("terminal_local", "status terminal_local", "usar terminal_local"), dangerous=True),), "Capacidade local terminal_local preparada. Confirmação obrigatória para ações perigosas.")
