from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class LaunchResult:
    success: bool
    application: str
    message: str


class ApplicationLauncher:
    def __init__(
        self,
        applications: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self._applications = applications or self._default_applications()

    def launch(
        self,
        application_name: str,
    ) -> LaunchResult:
        normalized_name = self._normalize(application_name)
        commands = self._applications.get(normalized_name)

        if commands is None:
            return LaunchResult(
                success=False,
                application=normalized_name,
                message=(
                    f"Não encontrei o aplicativo "
                    f"{application_name.strip()} configurado."
                ),
            )

        for command in commands:
            if self._try_launch(command):
                return LaunchResult(
                    success=True,
                    application=normalized_name,
                    message=(
                        f"Abrindo {self._display_name(normalized_name)}."
                    ),
                )

        return LaunchResult(
            success=False,
            application=normalized_name,
            message=(
                f"Não consegui abrir "
                f"{self._display_name(normalized_name)}."
            ),
        )

    def available_applications(self) -> tuple[str, ...]:
        return tuple(sorted(self._applications))

    def _try_launch(
        self,
        command: str,
    ) -> bool:
        try:
            if self._is_wsl():
                return self._launch_from_wsl(command)

            if platform.system() == "Windows":
                return self._launch_on_windows(command)

            return self._launch_on_linux(command)
        except (OSError, subprocess.SubprocessError):
            return False

    def _launch_from_wsl(
        self,
        command: str,
    ) -> bool:
        subprocess.Popen(
            [
                "cmd.exe",
                "/c",
                "start",
                "",
                command,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return True

    def _launch_on_windows(
        self,
        command: str,
    ) -> bool:
        os.startfile(command)
        return True

    def _launch_on_linux(
        self,
        command: str,
    ) -> bool:
        executable = shutil.which(command)

        if executable is None:
            path = Path(command)

            if not path.exists():
                return False

            executable = str(path)

        subprocess.Popen(
            [executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return True

    def _is_wsl(self) -> bool:
        if platform.system() != "Linux":
            return False

        release = platform.release().casefold()

        return (
            "microsoft" in release
            or "wsl" in release
            or "WSL_DISTRO_NAME" in os.environ
        )

    def _normalize(
        self,
        application_name: str,
    ) -> str:
        aliases = {
            "visual studio code": "vscode",
            "vs code": "vscode",
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
            "gerenciador de arquivos": "explorer",
            "terminal": "terminal",
            "prompt de comando": "terminal",
            "cmd": "terminal",
            "calculadora": "calculator",
            "bloco de notas": "notepad",
        }

        cleaned_name = application_name.strip().casefold()

        return aliases.get(cleaned_name, cleaned_name)

    def _display_name(
        self,
        application_name: str,
    ) -> str:
        display_names = {
            "vscode": "o Visual Studio Code",
            "discord": "o Discord",
            "spotify": "o Spotify",
            "opera": "o Opera GX",
            "chrome": "o Google Chrome",
            "edge": "o Microsoft Edge",
            "explorer": "o Explorador de Arquivos",
            "terminal": "o terminal",
            "calculator": "a calculadora",
            "notepad": "o Bloco de Notas",
        }

        return display_names.get(
            application_name,
            application_name,
        )

    def _default_applications(
        self,
    ) -> dict[str, tuple[str, ...]]:
        return {
            "vscode": (
                "code",
                "code.exe",
            ),
            "discord": (
                "discord",
                "Discord.exe",
            ),
            "spotify": (
                "spotify",
                "Spotify.exe",
            ),
            "opera": (
                "opera",
                "opera.exe",
                "launcher.exe",
            ),
            "chrome": (
                "chrome",
                "chrome.exe",
            ),
            "edge": (
                "msedge",
                "msedge.exe",
            ),
            "explorer": (
                "explorer.exe",
            ),
            "terminal": (
                "cmd.exe",
            ),
            "calculator": (
                "calc.exe",
            ),
            "notepad": (
                "notepad.exe",
            ),
        }