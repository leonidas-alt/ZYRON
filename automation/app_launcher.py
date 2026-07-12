from __future__ import annotations
import asyncio, subprocess, sys
from core.ports import ApplicationLauncher

class AppLauncher(ApplicationLauncher):
    CATALOG = {
        "vscode": {"linux": ["code"], "win32": ["code"], "darwin": ["code"]},
        "discord": {"linux": ["discord"], "win32": ["Discord"], "darwin": ["open", "-a", "Discord"]},
        "spotify": {"linux": ["spotify"], "win32": ["Spotify"], "darwin": ["open", "-a", "Spotify"]},
        "steam": {"linux": ["steam"], "win32": ["steam"], "darwin": ["open", "-a", "Steam"]},
        "terminal": {"linux": ["x-terminal-emulator"], "win32": ["cmd"], "darwin": ["open", "-a", "Terminal"]},
        "calculadora": {"linux": ["gnome-calculator"], "win32": ["calc"], "darwin": ["open", "-a", "Calculator"]},
        "explorer": {"linux": ["xdg-open", "."], "win32": ["explorer"], "darwin": ["open", "."]},
        "notepad": {"linux": ["gedit"], "win32": ["notepad"], "darwin": ["open", "-a", "TextEdit"]},
    }
    def normalize(self, app_name: str) -> str: return app_name.lower().replace(" ", "").replace("vs code", "vscode")
    def is_supported(self, app_name: str) -> bool: return self.normalize(app_name) in self.CATALOG
    async def open_application(self, app_name: str) -> None: await asyncio.to_thread(self._open_application, app_name)
    def _open_application(self, app_name: str) -> None:
        key = self.normalize(app_name)
        if key not in self.CATALOG: raise ValueError(f"Aplicativo não catalogado: {app_name}")
        cmd = self.CATALOG[key].get(sys.platform) or self.CATALOG[key].get("linux")
        subprocess.Popen(cmd, shell=False)
