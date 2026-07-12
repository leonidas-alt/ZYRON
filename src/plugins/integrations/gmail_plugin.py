from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("gmail", "Integração preparada para gmail"), (skill("gmail", ("gmail", "abrir gmail", "usar gmail")),), "gmail está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
