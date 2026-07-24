from __future__ import annotations

import re
import unicodedata

from zyron.application.commands.command_result import CommandResult
from zyron.infrastructure.automation.application_launcher import (
    ApplicationLauncher,
)


class ApplicationHandler:
    def __init__(
        self,
        application_launcher: ApplicationLauncher,
    ) -> None:
        self._application_launcher = application_launcher

    def handle(
        self,
        command: str,
    ) -> CommandResult:
        normalized_command = self._normalize(command)
        application_name = self._extract_application_name(
            normalized_command
        )

        if application_name is None:
            return CommandResult.not_handled()

        launch_result = self._application_launcher.launch(
            application_name
        )

        if launch_result.success:
            return CommandResult.success(
                message=launch_result.message,
                data={
                    "application": launch_result.application,
                },
            )

        return CommandResult.failure(
            message=launch_result.message,
            data={
                "application": launch_result.application,
            },
        )

    def _extract_application_name(
        self,
        command: str,
    ) -> str | None:
        patterns = (
            r"^abrir\s+(.+)$",
            r"^abra\s+(.+)$",
            r"^iniciar\s+(.+)$",
            r"^inicie\s+(.+)$",
            r"^executar\s+(.+)$",
            r"^execute\s+(.+)$",
        )

        for pattern in patterns:
            match = re.match(pattern, command)

            if match is not None:
                application_name = match.group(1).strip()

                if application_name:
                    return application_name

        return None

    def _normalize(
        self,
        command: str,
    ) -> str:
        cleaned_command = "".join(
            character
            for character in command
            if character.isprintable()
        )

        cleaned_command = unicodedata.normalize(
            "NFD",
            cleaned_command,
        )

        cleaned_command = "".join(
            character
            for character in cleaned_command
            if unicodedata.category(character) != "Mn"
        )

        cleaned_command = cleaned_command.casefold()

        cleaned_command = re.sub(
            r"[^a-z0-9\s]",
            " ",
            cleaned_command,
        )

        cleaned_command = re.sub(
            r"\s+",
            " ",
            cleaned_command,
        )

        return cleaned_command.strip()