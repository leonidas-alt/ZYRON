from __future__ import annotations

import asyncio
import subprocess

from core.ports import ApplicationLauncher


class AppLauncher(ApplicationLauncher):
    """Desktop automation adapter for launching local applications."""

    async def open_application(self, app_name: str) -> None:
        await asyncio.to_thread(self._open_application, app_name)

    @staticmethod
    def _open_application(app_name: str) -> None:
        subprocess.Popen(app_name, shell=True)  # noqa: S602 - intentional desktop automation hook
