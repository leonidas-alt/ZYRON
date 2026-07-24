from __future__ import annotations

import asyncio

from zyron.bootstrap.container import ApplicationContainer, build_container
from zyron.domain.exceptions import ZyronError


EXIT_COMMANDS = {
    "sair",
    "encerrar",
    "fechar",
    "exit",
    "quit",
}


async def run_text_cli(
    container: ApplicationContainer | None = None,
) -> None:
    app = container or build_container()
    name = app.settings.assistant_name

    print(f"\n{name} Online. Em que posso te ajudar?")
    print("Digite 'sair' para encerrar.\n")

    while True:
        try:
            user_input = await asyncio.to_thread(
                input,
                "> ",
            )

            command = user_input.strip()

            if not command:
                continue

            if command.casefold() in EXIT_COMMANDS:
                print("\nEncerrando. Até logo.")
                break

            response = await app.assistant.process(
                command
            )

            print(f"{response.text}\n")

        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando. Até logo.")
            break

        except ZyronError as error:
            print(f"{error}\n")

        except Exception as error:
            print(
                f"Erro inesperado: {error}\n"
            )


def main() -> None:
    asyncio.run(
        run_text_cli()
    )


if __name__ == "__main__":
    main()