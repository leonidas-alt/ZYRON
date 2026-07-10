from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("ram", "Capacidade local ram"), (skill("ram", ("ram", "status ram", "usar ram"), dangerous=False),), "Capacidade local ram preparada. Comando seguro recebido: {{target}}.")
