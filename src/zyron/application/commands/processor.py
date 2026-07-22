from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from zyron.application.commands.matcher import (
    CommandMatch,
    Intent,
)


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CommandResult:

    text: str
    source: str = "system"
    should_exit: bool = False
    success: bool = True


class AIClientProtocol(Protocol):

    async def generate(self, prompt: str) -> str:

        ...


class MemoryServiceProtocol(Protocol):

    def remember(self, key: str, value: str) -> None:

        ...

    def recall(self, key: str) -> str | None:

        ...

    def forget(self, key: str) -> bool:

        ...

    def list_all(self) -> list[dict[str, str]]:

        ...

    def save_interaction(
        self,
        user_text: str,
        assistant_text: str,
        source: str,
    ) -> None:

        ...


class ApplicationOpenerProtocol(Protocol):

    def open(self, application: str) -> str:
      
        ...


class CommandProcessor:

    def __init__(
        self,
        ai_client: AIClientProtocol,
        memory_service: MemoryServiceProtocol,
        application_opener: ApplicationOpenerProtocol | None = None,
        assistant_name: str = "ZYRON",
        owner_name: str = "usuário",
    ) -> None:

        self._ai_client = ai_client
        self._memory_service = memory_service
        self._application_opener = application_opener
        self._assistant_name = assistant_name.strip() or "ZYRON"
        self._owner_name = owner_name.strip() or "usuário"

    async def process(
        self,
        command: CommandMatch,
        raw_text: str = "",
    ) -> CommandResult:

        user_text = raw_text.strip()

        if not user_text:
            user_text = self._extract_original_text(command)

        logger.info(
            "Processando comando: intent=%s confidence=%.2f",
            command.intent.value,
            command.confidence,
        )

        try:
            result = await self._dispatch(
                command=command,
                user_text=user_text,
            )

        except ValueError as error:
            logger.warning(
                "Dados inválidos ao processar comando: %s",
                error,
            )

            result = CommandResult(
                text=str(error),
                source="validation",
                success=False,
            )

        except Exception:
            logger.exception(
                "Erro inesperado ao processar comando: %s",
                command.intent.value,
            )

            result = CommandResult(
                text=(
                    "Ocorreu um erro enquanto eu executava esse comando. "
                    "Verifique os logs do ZYRON para mais detalhes."
                ),
                source="error",
                success=False,
            )

        self._save_interaction_safely(
            user_text=user_text,
            result=result,
        )

        return result

    async def _dispatch(
        self,
        command: CommandMatch,
        user_text: str,
    ) -> CommandResult:

        match command.intent:
            case Intent.GET_TIME:
                return self._get_time()

            case Intent.SAVE_MEMORY:
                return self._save_memory(command)

            case Intent.RECALL_MEMORY:
                return await self._recall_memory(
                    command=command,
                    user_text=user_text,
                )

            case Intent.DELETE_MEMORY:
                return self._delete_memory(command)

            case Intent.LIST_MEMORIES:
                return self._list_memories()

            case Intent.OPEN_APPLICATION:
                return self._open_application(command)

            case Intent.EXIT:
                return self._exit()

            case Intent.CHAT:
                return await self._chat(
                    command=command,
                    user_text=user_text,
                )

            case Intent.UNKNOWN:
                return CommandResult(
                    text="Não recebi nenhum comando para executar.",
                    source="system",
                    success=False,
                )

            case _:
                return CommandResult(
                    text=(
                        "Eu identifiquei o comando, mas ainda não tenho "
                        "uma funcionalidade preparada para executá-lo."
                    ),
                    source="system",
                    success=False,
                )

    def _get_time(self) -> CommandResult:

        current_time = datetime.now().strftime("%H:%M")

        return CommandResult(
            text=f"Agora são {current_time}.",
            source="clock",
        )

    def _save_memory(
        self,
        command: CommandMatch,
    ) -> CommandResult:

        key = self._require_payload_value(
            command=command,
            field="key",
        )

        value = self._require_payload_value(
            command=command,
            field="value",
        )

        self._memory_service.remember(
            key=key,
            value=value,
        )

        logger.info(
            "Memória salva: key=%s",
            key,
        )

        return CommandResult(
            text=f"Certo. Vou lembrar que {key} é {value}.",
            source="memory",
        )

    async def _recall_memory(
        self,
        command: CommandMatch,
        user_text: str,
    ) -> CommandResult:

        key = self._require_payload_value(
            command=command,
            field="key",
        )

        value = self._memory_service.recall(key)

        if value is not None:
            return CommandResult(
                text=f"Eu lembro que {key} é {value}.",
                source="memory",
            )

        logger.info(
            "Memória não encontrada: key=%s",
            key,
        )

        return await self._chat(
            command=command,
            user_text=user_text,
        )

    def _delete_memory(
        self,
        command: CommandMatch,
    ) -> CommandResult:

        key = self._require_payload_value(
            command=command,
            field="key",
        )

        deleted = self._memory_service.forget(key)

        if deleted:
            logger.info(
                "Memória removida: key=%s",
                key,
            )

            return CommandResult(
                text=f"Certo. Esqueci a informação sobre {key}.",
                source="memory",
            )

        return CommandResult(
            text=f"Não encontrei nenhuma memória sobre {key}.",
            source="memory",
            success=False,
        )

    def _list_memories(self) -> CommandResult:

        memories = self._memory_service.list_all()

        if not memories:
            return CommandResult(
                text="Ainda não tenho nenhuma memória salva.",
                source="memory",
            )

        formatted_memories: list[str] = []

        for item in memories:
            key = item.get("key", "sem chave")
            value = item.get("value", "sem valor")

            formatted_memories.append(
                f"- {key}: {value}"
            )

        memories_text = "\n".join(formatted_memories)

        return CommandResult(
            text=f"Estas são as minhas memórias:\n{memories_text}",
            source="memory",
        )

    def _open_application(
        self,
        command: CommandMatch,
    ) -> CommandResult:

        application = self._require_payload_value(
            command=command,
            field="application",
        )

        if self._application_opener is None:
            return CommandResult(
                text=(
                    "A funcionalidade para abrir aplicativos ainda "
                    "não foi configurada no ZYRON."
                ),
                source="plugin",
                success=False,
            )

        response = self._application_opener.open(application)

        logger.info(
            "Solicitação de abertura de aplicativo: %s",
            application,
        )

        return CommandResult(
            text=response,
            source="application",
        )

    async def _chat(
        self,
        command: CommandMatch,
        user_text: str,
    ) -> CommandResult:

        prompt = command.payload.get("prompt", "").strip()

        if not prompt:
            prompt = user_text

        if not prompt:
            raise ValueError(
                "Não foi possível encontrar uma mensagem para enviar à IA."
            )

        system_context = self._build_system_context(
            user_message=prompt,
        )

        logger.info(
            "Enviando mensagem para o cliente de IA."
        )

        generated_response = await self._ai_client.generate(
            system_context
        )

        generated_response = generated_response.strip()

        if not generated_response:
            return CommandResult(
                text=(
                    "O modelo de inteligência artificial não devolveu "
                    "uma resposta."
                ),
                source="ai",
                success=False,
            )

        return CommandResult(
            text=generated_response,
            source="ai",
        )

    def _exit(self) -> CommandResult:
    
        return CommandResult(
            text=(
                f"{self._assistant_name} encerrando. "
                f"Até mais, {self._owner_name}."
            ),
            source="system",
            should_exit=True,
        )

    def _build_system_context(
        self,
        user_message: str,
    ) -> str:

        return (
            f"Você é {self._assistant_name}, um assistente pessoal "
            f"local criado para ajudar {self._owner_name}.\n\n"
            "Regras de comportamento:\n"
            "- Responda em português brasileiro.\n"
            "- Seja claro, direto e útil.\n"
            "- Não diga que executou ações que não foram executadas.\n"
            "- Não invente informações pessoais sobre o usuário.\n"
            "- Quando não souber algo, informe com honestidade.\n"
            "- Não realize ações perigosas ou proibidas.\n\n"
            f"Mensagem do usuário:\n{user_message}\n\n"
            f"Resposta de {self._assistant_name}:"
        )

    def _save_interaction_safely(
        self,
        user_text: str,
        result: CommandResult,
    ) -> None:

        if not user_text:
            return

        try:
            self._memory_service.save_interaction(
                user_text=user_text,
                assistant_text=result.text,
                source=result.source,
            )

        except Exception:
            logger.exception(
                "Não foi possível salvar a interação no histórico."
            )

    @staticmethod
    def _require_payload_value(
        command: CommandMatch,
        field: str,
    ) -> str:
      
        value = command.payload.get(field, "").strip()

        if not value:
            raise ValueError(
                f"O campo obrigatório '{field}' não foi informado."
            )

        return value

    @staticmethod
    def _extract_original_text(
        command: CommandMatch,
    ) -> str:

        if command.intent is Intent.CHAT:
            return command.payload.get("prompt", "").strip()

        if command.intent is Intent.OPEN_APPLICATION:
            application = command.payload.get(
                "application",
                "",
            )

            return f"abra {application}".strip()

        if command.intent is Intent.SAVE_MEMORY:
            key = command.payload.get("key", "")
            value = command.payload.get("value", "")

            return f"lembre que {key} é {value}".strip()

        if command.intent is Intent.RECALL_MEMORY:
            key = command.payload.get("key", "")

            return f"qual é {key}".strip()

        if command.intent is Intent.DELETE_MEMORY:
            key = command.payload.get("key", "")

            return f"esqueça {key}".strip()

        return command.intent.value
