class ZyronError(Exception):
    """Erro base conhecido do ZYRON."""


class AIUnavailableError(ZyronError):
    """A IA configurada não está disponível."""


class AIResponseError(ZyronError):
    """A IA retornou uma resposta inválida."""