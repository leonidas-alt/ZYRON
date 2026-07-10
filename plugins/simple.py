from __future__ import annotations

from domain.models import AssistantResponse, Capability, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface


class SimplePlugin(PluginInterface):
    def __init__(
        self,
        metadata: PluginMetadata,
        skill_defs: tuple[Skill, ...],
        response: str,
        credentials_required: bool = False,
    ) -> None:
        self.metadata = metadata
        self._skills = skill_defs
        self._response = response
        self._credentials_required = credentials_required
        self._skill_names = {skill.name for skill in skill_defs}

    def skills(self) -> tuple[Skill, ...]:
        return self._skills

    def can_handle(self, intent: CommandIntent) -> bool:
        return intent.skill_name in self._skill_names

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        if self._credentials_required:
            return AssistantResponse(
                f"{self.metadata.name} ainda precisa de credenciais no .env para executar este comando com segurança."
            )
        target = intent.target or intent.metadata.get("active_subject") or "isso"
        return AssistantResponse(self._response.format(target=target))


def skill(name: str, words: tuple[str, ...], dangerous: bool = False) -> Skill:
    return Skill(
        name=name,
        description=f"Comandos de {name}",
        examples=words,
        keywords=words,
        capability=Capability(name, f"Capacidade {name}", dangerous),
    )
