from __future__ import annotations

import asyncio

from zyron.bootstrap.container import ApplicationContainer, build_container
from zyron.domain.exceptions import ZyronError
from zyron.infrastructure.voice.exceptions import VoiceError


EXIT_COMMANDS = {
    "sair",
    "encerrar",
    "fechar",
    "exit",
    "quit",
}


async def run_voice_cli(
    container: ApplicationContainer | None = None,
) -> None:
    app = container or build_container()
    name = app.settings.assistant_name

    startup_message = (
        f"{name} Online. Em que posso te ajudar?"
    )

    print(f"\n{name} > {startup_message}")
    print("Pressione Enter para falar ou digite 'sair'.\n")

    await app.speech_synthesizer.speak(
        startup_message
    )

    while True:
        try:
            action = await asyncio.to_thread(
                input,
                "Enter para gravar > ",
            )

            if action.strip().casefold() in EXIT_COMMANDS:
                await _finish(app)
                break

            print(f"{name} > Ouvindo...")

            audio = await app.audio_capture.capture(
                duration_seconds=5.0
            )

            recognition = await app.speech_recognizer.recognize(
                audio
            )

            if not recognition.recognized:
                message = "Não consegui entender o que você disse."
                print(f"{name} > {message}\n")
                await app.speech_synthesizer.speak(message)
                continue

            recognized_text = recognition.text.strip()

            print(f"Você > {recognized_text}")

            if recognized_text.casefold() in EXIT_COMMANDS:
                await _finish(app)
                break

            if not app.wake_word_detector.detect(
                recognized_text
            ):
                wake_words = ", ".join(
                    app.wake_word_detector.wake_words
                )

                message = (
                    "Nenhuma palavra de ativação foi detectada. "
                    f"Diga {wake_words} antes do comando."
                )

                print(f"{name} > {message}\n")
                await app.speech_synthesizer.speak(message)
                continue

            command = app.wake_word_detector.extract_command(
                recognized_text
            )

            if not command:
                message = "Estou ouvindo. Pode dizer o comando."
                print(f"{name} > {message}\n")
                await app.speech_synthesizer.speak(message)
                continue

            if command.casefold() in EXIT_COMMANDS:
                await _finish(app)
                break

            response = await app.assistant.process(
                command
            )

            print(f"{name} > {response.text}\n")

            await app.speech_synthesizer.speak(
                response.text
            )

        except (EOFError, KeyboardInterrupt):
            await _finish(app)
            break

        except VoiceError as error:
            print(f"{name} > Erro de voz: {error}\n")

        except ZyronError as error:
            print(f"{name} > {error}\n")

        except Exception as error:
            print(f"{name} > Erro inesperado: {error}\n")


async def _finish(
    app: ApplicationContainer,
) -> None:
    message = "Encerrando. Até logo."

    print(
        f"\n{app.settings.assistant_name} > {message}"
    )

    try:
        await app.speech_synthesizer.speak(
            message
        )
    except VoiceError:
        pass
