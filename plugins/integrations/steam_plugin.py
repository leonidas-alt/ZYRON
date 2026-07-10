from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("steam", "Integração preparada para steam"), (skill("steam", ("steam", "abrir steam", "usar steam")),), "steam está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
