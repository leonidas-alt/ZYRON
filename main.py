from __future__ import annotations
import asyncio
from core.application import ZyronApplication
from core.config import Settings

def main() -> None:
    settings = Settings.from_env()
    app = ZyronApplication(settings=settings)
    asyncio.run(app.run())

if __name__ == "__main__":
    main()
