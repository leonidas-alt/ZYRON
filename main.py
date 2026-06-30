"""Application entrypoint for the ZYRON local assistant."""

from core.application import ZyronApplication
from core.config import Settings


def main() -> None:
    """Create and run the ZYRON application."""
    settings = Settings.from_env()
    app = ZyronApplication(settings=settings)
    app.run()


if __name__ == "__main__":
    main()
