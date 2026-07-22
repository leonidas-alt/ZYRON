from __future__ import annotations

import asyncio

from zyron.bootstrap.container import ApplicationContainer, build_container
from zyron.infrastructure.voice.exceptions import SpeechSynthesisError
from zyron.infrastructure.voice.speech_synthesizer import SpeechSynthesizer


EXIT_COMMANDS = {
    "sair",
    "encerrar",
    "fechar",
    "exit",
    "quit",
}


class VoiceCLI:
    def __init__(
        self,
        container: ApplicationContainer,
        synthesizer: SpeechSynthesizer,
    ) -> None:
        self._container = container
        self._synthesizer = synthesizer
        self._running = False

    async def run(self) -> None:
        self._running = True

        await self._show_startup_message()

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

        await self._show_shutdown_message()

    def stop(self) -> None:
        self._running = False

    async def _process_input(
        self,
        user_text: str,
    ) -> None:
        permission_result = self._container.permissions.check(
            user_text
        )

        if permission_result is not None:
            await self._respond(permission_result.message)
            return

        try:
            response = await self._container.assistant.process(
                user_text
            )
        except Exception as error:
            await self._respond(
                "Não consegui processar sua solicitação. "
                f"Erro: {error}"
            )
            return

        try:
            self._container.repository.save_interaction(
                user_text=user_text,
                assistant_text=response.text,
                source=response.source,
            )
        except Exception as error:
            print(
                "\nZYRON: Não foi possível salvar o histórico. "
                f"Erro: {error}\n"
            )

        await self._respond(response.text)

    async def _respond(
        self,
        text: str,
    ) -> None:
        assistant_name = (
            self._container.settings.assistant_name
        )

        print(f"\n{assistant_name}: {text}\n")

        try:
            await self._synthesizer.speak(text)
        except SpeechSynthesisError as error:
            print(
                f"{assistant_name}: Falha na reprodução de voz: "
                f"{error}\n"
            )

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
        normalized_text = user_text.casefold().strip()

        return normalized_text in EXIT_COMMANDS

    async def _show_startup_message(self) -> None:
        assistant_name = (
            self._container.settings.assistant_name
        )

        startup_message = (
            f"{assistant_name} Online. "
            "Em que posso te ajudar?"
        )

        print()
        print(startup_message)
        print("Digite 'sair' para encerrar.")
        print()

        try:
            await self._synthesizer.speak(
                startup_message
            )
        except SpeechSynthesisError as error:
            print(
                f"{assistant_name}: Falha na reprodução de voz: "
                f"{error}\n"
            )

    async def _show_shutdown_message(self) -> None:
        assistant_name = (
            self._container.settings.assistant_name
        )

        shutdown_message = "Sistema encerrado."

        print()
        print(f"{assistant_name}: {shutdown_message}")
        print()

        try:
            await self._synthesizer.speak(
                shutdown_message
            )
        except SpeechSynthesisError:
            pass


async def run_voice_cli(
    container: ApplicationContainer | None = None,
    synthesizer: SpeechSynthesizer | None = None,
) -> None:
    resolved_container = container or build_container()

    resolved_synthesizer = (
        synthesizer
        or SpeechSynthesizer(
            rate=180,
            volume=1.0,
        )
    )

    cli = VoiceCLI(
        container=resolved_container,
        synthesizer=resolved_synthesizer,
    )

    try:
        await cli.run()
    finally:
        try:
            resolved_synthesizer.stop()
        except SpeechSynthesisError:
            pass

        try:
            resolved_container.plugin_registry.disable_all()
        finally:
            resolved_container.repository.close()


def main() -> None:
    try:
        asyncio.run(run_voice_cli())
    except KeyboardInterrupt:
        print("\nZYRON: Sistema encerrado.")
    except Exception as error:
        raise SystemExit(
            f"Não foi possível iniciar o modo de voz: {error}"
        ) from error


if __name__ == "__main__":
    main()
