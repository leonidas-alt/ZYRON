from __future__ import annotations
from automation.app_launcher import AppLauncher
from domain.models import AssistantResponse, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface

class ApplicationPlugin(PluginInterface):
    metadata=PluginMetadata("application", "Controle seguro de aplicativos", capabilities=("applications",), dependencies=("application_launcher",))
    def __init__(self, application_launcher: AppLauncher) -> None: self._launcher = application_launcher
    def skills(self): return (Skill("application", "abrir aplicativos catalogados", ("abrir vscode", "abrir discord", "abrir spotify", "abrir steam", "abrir terminal", "abrir calculadora", "abrir explorer", "abrir notepad"), ("abrir", "executar", "vscode", "discord", "spotify", "steam", "terminal", "calculadora", "explorer", "notepad")),)
    def can_handle(self, intent: CommandIntent) -> bool: return intent.skill_name == "application"
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        app = (intent.target or intent.metadata.get("active_subject") or "").strip()
        if not app: return AssistantResponse("Qual aplicativo catalogado você quer abrir?")
        if not self._launcher.is_supported(app): return AssistantResponse(f"Não encontrei '{app}' no catálogo seguro de aplicativos.")
        try: await self._launcher.open_application(app)
        except Exception: return AssistantResponse(f"Não consegui abrir {app}. Verifique se está instalado.")
        return AssistantResponse(f"Abrindo aplicativo: {app}.")
def create_plugin(application_launcher: AppLauncher) -> PluginInterface: return ApplicationPlugin(application_launcher)
