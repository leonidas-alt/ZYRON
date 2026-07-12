from __future__ import annotations

import asyncio

from zyron.config.settings import Settings
from zyron.interfaces.text_cli import run_text_cli


async def run() -> None:
    settings = Settings.from_env()

    if settings.mode != "text":
        print(
            "O modo de voz ainda não foi implementado nesta versão. "
            "Iniciando o modo texto."
        )

    await run_text_cli()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()