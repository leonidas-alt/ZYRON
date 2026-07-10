from __future__ import annotations

from domain.models import AssistantResponse, Capability, CommandIntent, PluginMetadata, Skill
from domain.ports import PluginInterface


class SimplePlugin(PluginInterface):
    """Small adapter for prepared integrations that only return safe responses."""

    def __init__(
        self,
        metadata: PluginMetadata,
        skills: tuple[Skill, ...],
        response_template: str,
        credentials_required: bool = False,
    ) -> None:
        self.metadata = metadata
        self._skills = skills
        self._response_template = response_template
        self._credentials_required = credentials_required

    def skills(self) -> tuple[Skill, ...]:
        return self._skills

    def can_handle(self, intent: CommandIntent) -> bool:
        return intent.skill_name in {skill.name for skill in self._skills}

    async def execute(self, intent: CommandIntent) -> AssistantResponse:
        if self._credentials_required:
            return AssistantResponse(
                f"{self.metadata.name} ainda precisa de credenciais no .env "
                "para executar este comando com segurança."
            )
        target = intent.target or intent.metadata.get("active_subject") or "isso"
        return AssistantResponse(self._response_template.format(target=target))


def skill(name: str, words: tuple[str, ...], dangerous: bool = False) -> Skill:
    return Skill(
        name=name,
        description=f"Comandos de {name}",
        examples=words,
        keywords=words,
        capability=Capability(name, f"Capacidade {name}", dangerous),
    )
