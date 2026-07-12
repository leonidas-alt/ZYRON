from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("aws", "Integração preparada para aws"), (skill("aws", ("aws", "abrir aws", "usar aws")),), "aws está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
