from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("obs", "Integração preparada para obs"), (skill("obs", ("obs", "abrir obs", "usar obs")),), "obs está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
