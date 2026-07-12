from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("terminal", "Integração preparada para terminal"), (skill("terminal", ("terminal", "abrir terminal", "usar terminal")),), "terminal está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
