from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("docker", "Integração preparada para docker"), (skill("docker", ("docker", "abrir docker", "usar docker")),), "docker está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
