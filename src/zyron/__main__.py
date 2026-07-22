from __future__ import annotations

import asyncio
import sys

from zyron.bootstrap.container import build_container
from zyron.interfaces.text_cli import TextCLI


async def run() -> None:
    container = build_container()
    cli = TextCLI(container)

    try:
        await cli.run()
    finally:
        container.repository.close()
        container.plugin_registry.disable_all()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nZYRON: Sistema encerrado.")
    except Exception as error:
        print(
            f"\nZYRON: Não foi possível iniciar o sistema: {error}",
            file=sys.stderr,
        )
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
