from __future__ import annotations

import asyncio
import logging

from core.application import ApplicationContainer, build_voice_container
from core.config import Settings
from infrastructure.voice.exceptions import MicrophoneUnavailableError, VoiceError

logger = logging.getLogger(__name__)
EXIT_COMMANDS = {"sair", "encerrar", "desligar zyron"}
GREETING = "ZYRON online. Em que posso te ajudar?"


def resolve_wake_word(text: str, container: ApplicationContainer) -> str | None:
    if not container.settings.voice_require_wake_word:
        return text.strip()
    detector = container.wake_word_detector
    if detector is None or not detector.contains_wake_word(text):
        return None
    command = detector.remove_wake_word(text)
    return command or None


async def run_voice(container: ApplicationContainer | None = None, max_iterations: int | None = None) -> None:
    container = container or build_voice_container(Settings.from_env())
    await container.initialize()
    if container.audio_capture is None or container.speech_recognizer is None or container.speech_synthesizer is None:
        raise RuntimeError("Container de voz incompleto.")

    await container.speech_synthesizer.speak(GREETING)
    iterations = 0
    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        iterations += 1
        try:
            audio = await container.audio_capture.capture()
            text = await container.speech_recognizer.transcribe(audio)
            if not text:
                continue
            print(f"Você > {text}")
            normalized = text.lower().strip()
            if normalized in EXIT_COMMANDS:
                message = "Encerrando o ZYRON. Até logo."
                print(f"ZYRON > {message}")
                await container.speech_synthesizer.speak(message)
                break
            command_text = resolve_wake_word(text, container)
            if command_text is None:
                continue
            response = await container.command_processor.process(command_text)
            print(f"ZYRON > {response}")
            await container.speech_synthesizer.speak(response)
        except MicrophoneUnavailableError:
            message = "Não consegui acessar o microfone."
            print(f"ZYRON > {message}")
            await container.speech_synthesizer.speak(message)
        except VoiceError:
            logger.exception("Erro de voz no loop")
            message = "Ocorreu um erro no sistema de voz."
            print(f"ZYRON > {message}")
            await container.speech_synthesizer.speak(message)
        except Exception:
            logger.exception("Erro no loop de voz")
            message = "Ocorreu um erro ao processar seu comando."
            print(f"ZYRON > {message}")
            await container.speech_synthesizer.speak(message)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_voice())


if __name__ == "__main__":
    main()
