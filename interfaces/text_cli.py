from __future__ import annotations

import asyncio

from core.application import ZyronApplication, build_text_container
from core.config import Settings


async def run_text() -> None:
    settings = Settings.from_env()
    container = build_text_container(settings)
    await container.initialize()
    app = ZyronApplication(settings=settings, repository=container.repository, router=container.command_processor._router)
    while True:
        text = input("Você > ").strip()
        if text.lower() in {"sair", "encerrar"}:
            print("ZYRON > Encerrando o modo texto.")
            break
        print(f"ZYRON > {await app.process_text(text)}")


def main() -> None:
    asyncio.run(run_text())


if __name__ == "__main__":
    main()
