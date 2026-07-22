from __future__ import annotations

import asyncio

from zyron.bootstrap.container import ApplicationContainer, build_container
from zyron.infrastructure.voice.audio_capture import AudioCapture
from zyron.infrastructure.voice.exceptions import (
    AudioCaptureError,
    SpeechRecognitionError,
    SpeechSynthesisError,
    WakeWordDetectionError,
)
from zyron.infrastructure.voice.speech_recognizer import SpeechRecognizer
from zyron.infrastructure.voice.speech_synthesizer import SpeechSynthesizer
from zyron.infrastructure.voice.wake_word_detector import WakeWordDetector


EXIT_COMMANDS = {
    "sair",
    "encerrar",
    "desligar",
    "finalizar",
    "fechar zyron",
    "desligar zyron",
    "encerrar zyron",
    "exit",
    "quit",
}

SLEEP_COMMANDS = {
    "parar de ouvir",
    "pare de ouvir",
    "pode parar de ouvir",
    "voltar ao modo de espera",
    "volte ao modo de espera",
    "modo de espera",
    "ficar em espera",
    "fique em espera",
}


class VoiceCLI:
    def __init__(
        self,
        container: ApplicationContainer,
        audio_capture: AudioCapture,
        speech_recognizer: SpeechRecognizer,
        speech_synthesizer: SpeechSynthesizer,
        wake_word_detector: WakeWordDetector,
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
        self._wake_word_detector = wake_word_detector
        self._recording_duration_seconds = recording_duration_seconds
        self._running = False
        self._conversation_active = False

    async def run(self) -> None:
        self._running = True

        await self._show_startup_message()

        while self._running:
            try:
                recognized_text = await self._listen()
            except KeyboardInterrupt:
                self.stop()
                break

            if not recognized_text:
                continue

            print(f"\nVocê: {recognized_text}")

            normalized_text = self._normalize_command(
                recognized_text
            )

            if self._is_exit_command(normalized_text):
                self.stop()
                break

            if self._conversation_active:
                await self._handle_active_conversation(
                    recognized_text
                )
                continue

            await self._handle_waiting_mode(
                recognized_text
            )

        await self._show_shutdown_message()

    def stop(self) -> None:
        self._running = False
        self._conversation_active = False

    async def _handle_waiting_mode(
        self,
        recognized_text: str,
    ) -> None:
        try:
            wake_word_result = self._wake_word_detector.detect(
                recognized_text
            )
        except WakeWordDetectionError as error:
            print(
                f"\n{self._assistant_name}: "
                f"Não consegui verificar a palavra de ativação. "
                f"{error}"
            )
            return

        if not wake_word_result.detected:
            print(
                f"{self._assistant_name}: "
                "Aguardando a palavra de ativação."
            )
            return

        self._conversation_active = True

        if wake_word_result.has_command:
            command = wake_word_result.command.strip()

            if self._is_exit_command(
                self._normalize_command(command)
            ):
                self.stop()
                return

            await self._process_input(command)
            return

        await self._respond(
            "Estou ouvindo. Em que posso te ajudar?"
        )

    async def _handle_active_conversation(
        self,
        recognized_text: str,
    ) -> None:
        normalized_text = self._normalize_command(
            recognized_text
        )

        if self._is_sleep_command(normalized_text):
            self._conversation_active = False

            await self._respond(
                "Certo. Voltando ao modo de espera."
            )
            return

        try:
            wake_word_result = self._wake_word_detector.detect(
                recognized_text
            )
        except WakeWordDetectionError:
            wake_word_result = None

        if (
            wake_word_result is not None
            and wake_word_result.detected
            and wake_word_result.has_command
        ):
            recognized_text = wake_word_result.command

        await self._process_input(
            recognized_text
        )

    async def _listen(self) -> str:
        if self._conversation_active:
            status_message = (
                f"{self._assistant_name}: Estou ouvindo por "
                f"{self._recording_duration_seconds:.0f} segundos..."
            )
        else:
            status_message = (
                f"{self._assistant_name}: Aguardando a palavra "
                "de ativação..."
            )

        print(f"\n{status_message}")

        try:
            audio = await self._audio_capture.record(
                duration_seconds=self._recording_duration_seconds,
            )
        except AudioCaptureError as error:
            print(
                f"\n{self._assistant_name}: "
                f"Não consegui acessar o microfone. {error}"
            )

            await asyncio.sleep(1)
            return ""

        print(
            f"{self._assistant_name}: "
            "Processando sua fala..."
        )

        try:
            result = await self._speech_recognizer.recognize(
                audio
            )
        except SpeechRecognitionError as error:
            print(
                f"\n{self._assistant_name}: "
                f"Não consegui reconhecer sua fala. {error}"
            )

            await asyncio.sleep(1)
            return ""

        if not result.recognized:
            print(
                f"\n{self._assistant_name}: "
                "Nenhuma fala foi reconhecida."
            )
            return ""

        return result.text.strip()

    async def _process_input(
        self,
        user_text: str,
    ) -> None:
        cleaned_text = user_text.strip()

        if not cleaned_text:
            return

        normalized_text = self._normalize_command(
            cleaned_text
        )

        if self._is_sleep_command(normalized_text):
            self._conversation_active = False

            await self._respond(
                "Certo. Voltando ao modo de espera."
            )
            return

        permission_result = self._container.permissions.check(
            cleaned_text
        )

        if permission_result is not None:
            await self._respond(
                permission_result.message
            )
            return

        try:
            response = await self._container.assistant.process(
                cleaned_text
            )
        except Exception as error:
            await self._respond(
                "Não consegui processar sua solicitação. "
                f"Erro: {error}"
            )
            return

        try:
            self._container.repository.save_interaction(
                user_text=cleaned_text,
                assistant_text=response.text,
                source=response.source,
            )
        except Exception as error:
            print(
                f"\n{self._assistant_name}: "
                "Não foi possível salvar o histórico. "
                f"Erro: {error}"
            )

        await self._respond(
            response.text
        )

    async def _respond(
        self,
        text: str,
    ) -> None:
        cleaned_text = text.strip()

        if not cleaned_text:
            return

        print(
            f"\n{self._assistant_name}: "
            f"{cleaned_text}\n"
        )

        try:
            await self._speech_synthesizer.speak(
                cleaned_text
            )
        except SpeechSynthesisError as error:
            print(
                f"{self._assistant_name}: "
                "Não consegui reproduzir a resposta por voz. "
                f"{error}"
            )

    async def _show_startup_message(self) -> None:
        startup_message = (
            f"{self._assistant_name} Online. "
            "Em que posso te ajudar?"
        )

        print()
        print(startup_message)
        print(
            "Diga 'Zyron' para ativar o modo de conversa."
        )
        print(
            "Diga 'pare de ouvir' para voltar ao modo de espera."
        )
        print(
            "Diga 'desligar Zyron' para encerrar o sistema."
        )

        try:
            await self._speech_synthesizer.speak(
                startup_message
            )
        except SpeechSynthesisError as error:
            print(
                f"\n{self._assistant_name}: "
                "Não consegui reproduzir a mensagem inicial. "
                f"{error}"
            )

    async def _show_shutdown_message(self) -> None:
        shutdown_message = "Sistema encerrado."

        print()
        print(
            f"{self._assistant_name}: "
            f"{shutdown_message}"
        )

        try:
            await self._speech_synthesizer.speak(
                shutdown_message
            )
        except SpeechSynthesisError:
            pass

    def _is_exit_command(
        self,
        normalized_text: str,
    ) -> bool:
        return normalized_text in EXIT_COMMANDS

    def _is_sleep_command(
        self,
        normalized_text: str,
    ) -> bool:
        return normalized_text in SLEEP_COMMANDS

    def _normalize_command(
        self,
        text: str,
    ) -> str:
        return " ".join(
            text.casefold().strip().split()
        )

    @property
    def _assistant_name(self) -> str:
        return self._container.settings.assistant_name


async def run_voice_cli(
    container: ApplicationContainer | None = None,
    audio_capture: AudioCapture | None = None,
    speech_recognizer: SpeechRecognizer | None = None,
    speech_synthesizer: SpeechSynthesizer | None = None,
    wake_word_detector: WakeWordDetector | None = None,
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

    resolved_wake_word_detector = (
        wake_word_detector
        or WakeWordDetector(
            wake_words=(
                "zyron",
                "ziron",
                "sairon",
            )
        )
    )

    cli = VoiceCLI(
        container=resolved_container,
        audio_capture=resolved_audio_capture,
        speech_recognizer=resolved_speech_recognizer,
        speech_synthesizer=resolved_speech_synthesizer,
        wake_word_detector=resolved_wake_word_detector,
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
        asyncio.run(
            run_voice_cli()
        )
    except KeyboardInterrupt:
        print(
            "\nZYRON: Sistema encerrado."
        )
    except Exception as error:
        raise SystemExit(
            "Não foi possível iniciar o modo de voz: "
            f"{error}"
        ) from error


if __name__ == "__main__":
    main()
