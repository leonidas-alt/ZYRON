from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("linux", "Integração preparada para linux"), (skill("linux", ("linux", "abrir linux", "usar linux")),), "linux está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
