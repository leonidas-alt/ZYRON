from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("git", "Integração preparada para git"), (skill("git", ("git", "abrir git", "usar git")),), "git está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
