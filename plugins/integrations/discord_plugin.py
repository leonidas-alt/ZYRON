from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("discord", "Integração preparada para discord"), (skill("discord", ("discord", "abrir discord", "usar discord")),), "discord está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
