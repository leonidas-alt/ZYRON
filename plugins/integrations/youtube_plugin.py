from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("youtube", "Integração preparada para youtube"), (skill("youtube", ("youtube", "abrir youtube", "usar youtube")),), "youtube está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
