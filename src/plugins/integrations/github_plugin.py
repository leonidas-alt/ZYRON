from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("github", "Integração preparada para github"), (skill("github", ("github", "abrir github", "usar github")),), "github está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
