from core.models import CommandIntent, CommandType

class CommandInterpreter:

    def interpret(self, text: str) -> CommandIntent:
        normalized = text.lower().strip()
        if normalized.startswith("abrir aplicativo "):
            return CommandIntent(CommandType.OPEN_APP, text, normalized.replace("abrir aplicativo ", "", 1))
        if normalized.startswith("abrir site "):
            return CommandIntent(CommandType.OPEN_SITE, text, normalized.replace("abrir site ", "", 1))
        if normalized.startswith("pesquisar ") or normalized.startswith("pesquise "):
            query = normalized.replace("pesquisar ", "", 1).replace("pesquise ", "", 1)
            return CommandIntent(CommandType.GOOGLE_SEARCH, text, query)
        if "horas" in normalized or "horário" in normalized:
            return CommandIntent(CommandType.CURRENT_TIME, text)
        if "temperatura" in normalized or "clima" in normalized:
            return CommandIntent(CommandType.CURRENT_WEATHER, text)
        if normalized:
            return CommandIntent(CommandType.AI_CHAT, text)
        return CommandIntent(CommandType.UNKNOWN, text)
