from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Sequence

from zyron.bootstrap.container import build_container
from zyron.interfaces.text_cli import TextCLI
from zyron.interfaces.voice_cli import VoiceCLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zyron",
        description="Assistente pessoal ZYRON.",
    )

    mode_group = parser.add_mutually_exclusive_group()

    mode_group.add_argument(
        "--text",
        action="store_true",
        help="Inicia o ZYRON no modo texto.",
    )

    mode_group.add_argument(
        "--voice",
        action="store_true",
        help="Inicia o ZYRON no modo voz.",
    )

    return parser


async def run_text_mode() -> None:
    container = build_container()

    cli = TextCLI(
        container=container,
    )

    try:
        await cli.run()
    finally:
        try:
            container.plugin_registry.disable_all()
        finally:
            container.repository.close()


async def run_voice_mode() -> None:
    container = build_container()

    if not container.settings.voice_enabled:
        container.repository.close()

        raise RuntimeError(
            "O modo de voz está desativado nas configurações."
        )

    cli = VoiceCLI(
        container=container,
        audio_capture=container.audio_capture,
        speech_recognizer=container.speech_recognizer,
        speech_synthesizer=container.speech_synthesizer,
        wake_word_detector=container.wake_word_detector,
        recording_duration_seconds=(
            container.settings.recording_duration_seconds
        ),
    )

    try:
        await cli.run()
    finally:
        try:
            container.speech_synthesizer.stop()
        except Exception:
            pass

        try:
            container.plugin_registry.disable_all()
        finally:
            container.repository.close()


async def run(
    arguments: argparse.Namespace,
) -> None:
    if arguments.voice:
        await run_voice_mode()
        return

    await run_text_mode()


def main(
    argv: Sequence[str] | None = None,
) -> None:
    parser = build_parser()
    arguments = parser.parse_args(argv)

    try:
        asyncio.run(
            run(arguments)
        )
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
