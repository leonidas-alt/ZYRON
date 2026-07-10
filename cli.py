from __future__ import annotations
import asyncio
from core.application import ZyronApplication
from core.config import Settings

_EXIT_COMMANDS = {"sair", "exit", "quit"}

async def run_cli() -> None:
    settings = Settings.from_env()
    app = ZyronApplication(settings=settings)
    await app.repository.initialize()

    print(f"{settings.assistant_name} pronto. Digite 'sair' para encerrar.")
    while True:
        command_text = input("Você: ").strip()
        if command_text.lower() in _EXIT_COMMANDS:
            print(f"{settings.assistant_name}: Até logo.")
            break
        if not command_text:
            continue

        response = await app.process_text(command_text)
        print(f"ZYRON: {response}")

def main() -> None:
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
