from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("windows", "Integração preparada para windows"), (skill("windows", ("windows", "abrir windows", "usar windows")),), "windows está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
