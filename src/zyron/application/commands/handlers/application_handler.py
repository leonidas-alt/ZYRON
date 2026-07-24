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

        application_name = self._remove_articles(
            application_name
        )

        resolved_application = self._resolve_application(
            application_name
        )

        if resolved_application is None:
            return CommandResult.not_handled()

        launch_result = self._application_launcher.launch(
            resolved_application
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
            r"^(?:por favor\s+)?abrir\s+(.+)$",
            r"^(?:por favor\s+)?abra\s+(.+)$",
            r"^(?:por favor\s+)?iniciar\s+(.+)$",
            r"^(?:por favor\s+)?inicie\s+(.+)$",
            r"^(?:por favor\s+)?executar\s+(.+)$",
            r"^(?:por favor\s+)?execute\s+(.+)$",
        )

        for pattern in patterns:
            match = re.match(
                pattern,
                command,
            )

            if match is None:
                continue

            application_name = match.group(1).strip()

            if application_name:
                return application_name

        return None

    def _remove_articles(
        self,
        application_name: str,
    ) -> str:
        return re.sub(
            r"^(?:o|a|os|as|um|uma)\s+",
            "",
            application_name,
        ).strip()

    def _resolve_application(
        self,
        application_name: str,
    ) -> str | None:
        aliases = {
            "visual studio code": "vscode",
            "vs code": "vscode",
            "vscode": "vscode",
            "code": "vscode",
            "discord": "discord",
            "spotify": "spotify",
            "opera": "opera",
            "opera gx": "opera",
            "google chrome": "chrome",
            "chrome": "chrome",
            "microsoft edge": "edge",
            "edge": "edge",
            "explorador de arquivos": "explorer",
            "explorador": "explorer",
            "explorer": "explorer",
            "gerenciador de arquivos": "explorer",
            "terminal": "terminal",
            "prompt de comando": "terminal",
            "cmd": "terminal",
            "calculadora": "calculator",
            "calculator": "calculator",
            "bloco de notas": "notepad",
            "notepad": "notepad",
        }

        resolved_application = aliases.get(
            application_name
        )

        if resolved_application is None:
            return None

        available_applications = set(
            self._application_launcher.available_applications()
        )

        if resolved_application not in available_applications:
            return None

        return resolved_application

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