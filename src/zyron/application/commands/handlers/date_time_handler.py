from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

from zyron.application.commands.command_result import CommandResult


class DateTimeHandler:
    def __init__(
        self,
        timezone_name: str = "America/Sao_Paulo",
    ) -> None:
        self._timezone = ZoneInfo(timezone_name)

    def handle(
        self,
        command: str,
    ) -> CommandResult:
        normalized_command = self._normalize(command)

        if not normalized_command:
            return CommandResult.not_handled()

        if self._is_date_command(normalized_command):
            return self._build_date_result()

        if self._is_time_command(normalized_command):
            return self._build_time_result()

        return CommandResult.not_handled()

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

    def _is_date_command(
        self,
        command: str,
    ) -> bool:
        date_commands = {
            "que dia e hoje",
            "qual e a data de hoje",
            "qual a data de hoje",
            "data de hoje",
            "me diga a data de hoje",
            "me fale a data de hoje",
            "em que dia estamos",
            "qual dia e hoje",
            "qual dia estamos",
        }

        return command in date_commands

    def _is_time_command(
        self,
        command: str,
    ) -> bool:
        time_commands = {
            "que horas sao",
            "qual e o horario",
            "qual o horario",
            "me diga as horas",
            "me fale as horas",
            "que horas sao agora",
            "qual e a hora",
            "qual a hora",
        }

        return command in time_commands

    def _build_date_result(
        self,
    ) -> CommandResult:
        now = datetime.now(self._timezone)

        weekdays = {
            0: "segunda-feira",
            1: "terça-feira",
            2: "quarta-feira",
            3: "quinta-feira",
            4: "sexta-feira",
            5: "sábado",
            6: "domingo",
        }

        months = {
            1: "janeiro",
            2: "fevereiro",
            3: "março",
            4: "abril",
            5: "maio",
            6: "junho",
            7: "julho",
            8: "agosto",
            9: "setembro",
            10: "outubro",
            11: "novembro",
            12: "dezembro",
        }

        weekday = weekdays[now.weekday()]
        month = months[now.month]

        message = (
            f"Hoje é {weekday}, "
            f"{now.day} de {month} de {now.year}."
        )

        return CommandResult.success(
            message=message,
            data={
                "date": now.date().isoformat(),
                "weekday": weekday,
                "timezone": str(self._timezone),
            },
        )

    def _build_time_result(
        self,
    ) -> CommandResult:
        now = datetime.now(self._timezone)

        message = (
            f"Agora são {now.hour:02d} horas "
            f"e {now.minute:02d} minutos."
        )

        return CommandResult.success(
            message=message,
            data={
                "time": now.time().isoformat(
                    timespec="minutes"
                ),
                "timezone": str(self._timezone),
            },
        )