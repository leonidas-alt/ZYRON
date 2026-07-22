from __future__ import annotations

import asyncio

from zyron.bootstrap.container import ApplicationContainer, build_container


EXIT_COMMANDS = {
    "sair",
    "encerrar",
    "fechar",
    "exit",
    "quit",
}


class TextCLI:
    def __init__(
        self,
        container: ApplicationContainer,
    ) -> None:
        self._container = container
        self._running = False

    async def run(self) -> None:
        self._running = True

        self._show_startup_message()

        while self._running:
            try:
                user_text = await self._read_input()
            except (EOFError, KeyboardInterrupt):
                self.stop()
                break

            if not user_text:
                continue

            if self._is_exit_command(user_text):
                self.stop()
                break

            await self._process_input(user_text)

        self._show_shutdown_message()

    def stop(self) -> None:
        self._running = False

    async def _process_input(
        self,
        user_text: str,
    ) -> None:
        permission_result = self._container.permissions.check(user_text)

        if permission_result is not None:
            print(f"\nZYRON: {permission_result.message}\n")
            return

        try:
            response = await self._container.assistant.process(user_text)
        except Exception as error:
            print(
                "\nZYRON: Não consegui processar sua solicitação. "
                f"Erro: {error}\n"
            )
            return

        self._container.repository.save_interaction(
            user_text=user_text,
            assistant_text=response.text,
            source=response.source,
        )

        print(f"\nZYRON: {response.text}\n")

    async def _read_input(self) -> str:
        user_text = await asyncio.to_thread(
            input,
            "Você: ",
        )

        return user_text.strip()

    def _is_exit_command(
        self,
        user_text: str,
    ) -> bool:
        return user_text.lower().strip() in EXIT_COMMANDS

    def _show_startup_message(self) -> None:
        assistant_name = self._container.settings.assistant_name

        print()
        print(f"{assistant_name} Online. Em que posso te ajudar?")
        print("Digite 'sair' para encerrar.")
        print()

    def _show_shutdown_message(self) -> None:
        assistant_name = self._container.settings.assistant_name

        print()
        print(f"{assistant_name}: Sistema encerrado.")
        print()


async def run_text_cli(
    container: ApplicationContainer | None = None,
) -> None:
    resolved_container = container or build_container()

    cli = TextCLI(resolved_container)

    await cli.run()


def main() -> None:
    asyncio.run(run_text_cli())


if __name__ == "__main__":
    main()
