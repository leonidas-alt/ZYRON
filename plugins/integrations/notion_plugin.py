from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("notion", "Integração preparada para notion"), (skill("notion", ("notion", "abrir notion", "usar notion")),), "notion está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
