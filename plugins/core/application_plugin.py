from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("application", "Controle de aplicativos"), (skill("application", ("abrir aplicativo", "abra", "executar aplicativo", "spotify")),), "Abrindo/preparando aplicativo: {target}.")
