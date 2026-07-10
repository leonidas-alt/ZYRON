from plugins.simple import SimplePlugin, skill
from domain.models import PluginMetadata
from domain.ports import PluginInterface

def create_plugin() -> PluginInterface:
    return SimplePlugin(PluginMetadata("ai", "Fallback para IA local/Ollama"), (skill("ai_chat", ("converse", "pergunta", "explique")),), "Ainda não conectei a IA local para responder: {target}")
