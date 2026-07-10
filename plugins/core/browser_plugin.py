import webbrowser
from domain.models import AssistantResponse, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface
class BrowserPlugin(PluginInterface):
    metadata=PluginMetadata("browser", "Navegação web local")
    def skills(self): return (Skill("browser", "abrir sites e pesquisar", ("abrir site", "pesquisar", "busque"), ("site", "pesquisar", "google", "navegador")),)
    def can_handle(self, intent: CommandIntent) -> bool: return intent.skill_name == "browser"
    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        target= intent.target or ""
        if target: webbrowser.open(target if target.startswith(("http://","https://")) else f"https://www.google.com/search?q={target}")
        return AssistantResponse(f"Abrindo no navegador: {target or intent.raw_text}.")
def create_plugin() -> PluginInterface: return BrowserPlugin()
