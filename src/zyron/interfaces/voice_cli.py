from __future__ import annotations

import asyncio

from zyron.bootstrap.container import ApplicationContainer, build_container
from zyron.infrastructure.voice.audio_capture import AudioCapture
from zyron.infrastructure.voice.exceptions import (
    AudioCaptureError,
    SpeechRecognitionError,
    SpeechSynthesisError,
)
from zyron.infrastructure.voice.speech_recognizer import SpeechRecognizer
from zyron.infrastructure.voice.speech_synthesizer import SpeechSynthesizer


EXIT_COMMANDS = {
    "sair",
    "encerrar",
    "fechar",
    "desligar",
    "finalizar",
    "exit",
    "quit",
}


class VoiceCLI:
    def __init__(
        self,
        container: ApplicationContainer,
        audio_capture: AudioCapture,
        speech_recognizer: SpeechRecognizer,
        speech_synthesizer: SpeechSynthesizer,
        recording_duration_seconds: float = 5.0,
    ) -> None:
        if recording_duration_seconds <= 0:
            raise ValueError(
                "A duração da gravação deve ser maior que zero."
            )

        self._container = container
        self._audio_capture = audio_capture
        self._speech_recognizer = speech_recognizer
        self._speech_synthesizer = speech_synthesizer
        self._recording_duration_seconds = recording_duration_seconds
        self._running = False

    async def run(self) -> None:
        self._running = True

        await self._show_startup_message()

        while self._running:
            try:
                user_text = await self._listen()
            except KeyboardInterrupt:
                self.stop()
                break

            if not user_text:
                continue

            print(f"\nVocê: {user_text}")

            if self._is_exit_command(user_text):
                self.stop()
                break

            await self._process_input(user_text)

        await self._show_shutdown_message()

    def stop(self) -> None:
        self._running = False

    async def _listen(self) -> str:
        assistant_name = self._container.settings.assistant_name

        print(
            f"\n{assistant_name}: Estou ouvindo por "
            f"{self._recording_duration_seconds:.0f} segundos..."
        )

        try:
            audio = await self._audio_capture.record(
                duration_seconds=self._recording_duration_seconds,
            )
        except AudioCaptureError as error:
            print(
                f"\n{assistant_name}: Não consegui acessar o microfone. "
                f"{error}"
            )
            await asyncio.sleep(1)
            return ""

        print(f"{assistant_name}: Processando sua fala...")

        try:
            result = await self._speech_recognizer.recognize(audio)
        except SpeechRecognitionError as error:
            print(
                f"\n{assistant_name}: Não consegui reconhecer sua fala. "
                f"{error}"
            )
            await asyncio.sleep(1)
            return ""

        if not result.recognized:
            print(
                f"\n{assistant_name}: Não consegui entender o que foi dito."
            )
            return ""

        return result.text.strip()

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
            assistant_name = (
                self._container.settings.assistant_name
            )

            print(
                f"\n{assistant_name}: Não foi possível salvar "
                f"o histórico. Erro: {error}"
            )

        await self._respond(response.text)

    async def _respond(
        self,
        text: str,
    ) -> None:
        cleaned_text = text.strip()

        if not cleaned_text:
            return

        assistant_name = self._container.settings.assistant_name

        print(f"\n{assistant_name}: {cleaned_text}\n")

        try:
            await self._speech_synthesizer.speak(cleaned_text)
        except SpeechSynthesisError as error:
            print(
                f"{assistant_name}: Não consegui reproduzir "
                f"a resposta por voz. {error}"
            )

    def _is_exit_command(
        self,
        user_text: str,
    ) -> bool:
        normalized_text = user_text.casefold().strip()

        return normalized_text in EXIT_COMMANDS

    async def _show_startup_message(self) -> None:
        assistant_name = self._container.settings.assistant_name

        startup_message = (
            f"{assistant_name} Online. Em que posso te ajudar?"
        )

        print()
        print(startup_message)
        print(
            "Fale 'sair', 'encerrar' ou 'desligar' "
            "para finalizar."
        )

        try:
            await self._speech_synthesizer.speak(
                startup_message
            )
        except SpeechSynthesisError as error:
            print(
                f"\n{assistant_name}: Não consegui reproduzir "
                f"a mensagem inicial. {error}"
            )

    async def _show_shutdown_message(self) -> None:
        assistant_name = self._container.settings.assistant_name
        shutdown_message = "Sistema encerrado."

        print()
        print(f"{assistant_name}: {shutdown_message}")

        try:
            await self._speech_synthesizer.speak(
                shutdown_message
            )
        except SpeechSynthesisError:
            pass


async def run_voice_cli(
    container: ApplicationContainer | None = None,
    audio_capture: AudioCapture | None = None,
    speech_recognizer: SpeechRecognizer | None = None,
    speech_synthesizer: SpeechSynthesizer | None = None,
) -> None:
    resolved_container = container or build_container()

    resolved_audio_capture = (
        audio_capture
        or AudioCapture(
            sample_rate=16_000,
            channels=1,
            dtype="int16",
        )
    )

    resolved_speech_recognizer = (
        speech_recognizer
        or SpeechRecognizer(
            model_path="models/vosk-pt",
        )
    )

    resolved_speech_synthesizer = (
        speech_synthesizer
        or SpeechSynthesizer(
            rate=180,
            volume=1.0,
        )
    )

    cli = VoiceCLI(
        container=resolved_container,
        audio_capture=resolved_audio_capture,
        speech_recognizer=resolved_speech_recognizer,
        speech_synthesizer=resolved_speech_synthesizer,
        recording_duration_seconds=5.0,
    )

    try:
        await cli.run()
    finally:
        try:
            resolved_speech_synthesizer.stop()
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
