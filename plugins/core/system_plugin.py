from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("system", "Comandos de sistema seguros"), (skill("system", ("status", "sistema", "cpu", "ram", "disco", "bateria")),), "Sistema pronto. Comandos perigosos exigem confirmação antes de executar.")
