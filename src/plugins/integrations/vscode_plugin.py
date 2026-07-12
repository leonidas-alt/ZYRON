from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("vscode", "Integração preparada para vscode"), (skill("vscode", ("vscode", "abrir vscode", "usar vscode")),), "vscode está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
