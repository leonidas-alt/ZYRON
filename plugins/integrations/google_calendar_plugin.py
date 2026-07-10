from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("google_calendar", "Integração preparada para google_calendar"), (skill("google_calendar", ("google_calendar", "abrir google_calendar", "usar google_calendar")),), "google_calendar está preparado, mas precisa de credenciais/configuração no .env quando aplicável.", credentials_required=True)
