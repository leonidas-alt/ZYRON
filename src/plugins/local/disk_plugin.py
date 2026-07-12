from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("disk", "Capacidade local disk"), (skill("disk", ("disk", "status disk", "usar disk"), dangerous=False),), "Capacidade local disk preparada. Comando seguro recebido: {{target}}.")
