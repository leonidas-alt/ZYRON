import subprocess


class AppLauncher:

    def open_application(self, app_name: str) -> None:
        """Launch an application without blocking the assistant loop."""
        subprocess.Popen(app_name, shell=True)  # noqa: S602 - intended desktop automation hook
