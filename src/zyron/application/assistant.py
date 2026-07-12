from __future__ import annotations

from zyron.domain.models import AssistantResponse
from zyron.domain.ports import AIClient


class ZyronAssistant:
    def __init__(
        self,
        ai_client: AIClient,
        assistant_name: str,
        owner_name: str,
    ) -> None:
        self._ai_client = ai_client
        self._assistant_name = assistant_name
        self._owner_name = owner_name

    async def process(self, user_text: str) -> AssistantResponse:
        cleaned_text = user_text.strip()

        if not cleaned_text:
            return AssistantResponse(
                text="Não recebi nenhum comando.",
                source="system",
            )

        prompt = self._build_prompt(cleaned_text)
        generated_text = await self._ai_client.generate(prompt)

        return AssistantResponse(
            text=generated_text,
            source="ollama",
        )

    def _build_prompt(self, user_text: str) -> str:
        return f"""
Você é {self._assistant_name}, assistente pessoal de {self._owner_name}.

Características:
- amigável e descontraído em conversas comuns;
- futurista e objetivo ao executar comandos;
- técnico e detalhado ao tratar programação;
- paciente e didático ao ensinar;
- responda em português brasileiro;
- não diga que executou uma ação que não foi realmente executada;
- não invente resultados, arquivos, comandos executados ou integrações.

Usuário: {user_text}
{self._assistant_name}:
""".strip()