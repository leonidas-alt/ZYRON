from __future__ import annotations

import asyncio
import sys

from zyron.bootstrap.container import build_container
from zyron.domain.exceptions import ZyronError
from zyron.infrastructure.voice.exceptions import VoiceError
from zyron.interfaces.text_cli import run_text_cli
from zyron.interfaces.voice_cli import run_voice_cli


async def run() -> None:
    container = build_container()

    mode = container.settings.mode.strip().casefold()

    if mode == "voice":
        await run_voice_cli(container)
        return

    if mode == "text":
        await run_text_cli(container)
        return

    raise ValueError(
        f"Modo de execução inválido: {container.settings.mode}"
    )


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nZYRON encerrado.")
    except (VoiceError, ZyronError, ValueError) as error:
        print(f"Erro ao iniciar o ZYRON: {error}")
        sys.exit(1)
    except Exception as error:
        print(f"Erro inesperado ao iniciar o ZYRON: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
