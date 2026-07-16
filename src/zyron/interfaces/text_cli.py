from __future__ import annotations

from datetime import datetime

from zyron.bootstrap.container import ApplicationContainer, build_container
from zyron.domain.exceptions import ZyronError


EXIT_COMMANDS = {
    "sair",
    "encerrar",
    "fechar",
    "exit",
    "quit",
}

def build_startup_message(name: str) -> str:
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    hour = now.hour

    if 5 <= hour < 12:
        greeting = "Bom dia"
    elif 12 <= hour < 18:
        greeting = "Boa tarde"
    else: 
        greeting = "Boa noite"
    
    return (
        f"{name} online."
        f"\n{greeting}, Leonidas."
        f"\nAgora são {current_time}."
        "\nO que gostaria de fazer?"
        "\nVai estudar, programar ou jogar?"
    )

async def run_text_cli(
    container: ApplicationContainer | None = None,
) -> None:
    app = container or build_container()
    name = app.settings.assistant_name

    startup_message = build_startup_message(name)

    print(f"\n{startup_message}")
    print("Digite 'sair' para encerrar.\n")

    while True:
        try:
            user_text = input("Você > ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{name} > Encerrando. Até logo.")
            break

        if not user_text:
            continue

        if user_text.lower() in EXIT_COMMANDS:
            print(f"{name} > Encerrando. Até logo.")
            break

        try:
            response = await app.assistant.process(user_text)
            print(f"{name} > {response.text}\n")

        except ZyronError as exc:
            print(f"{name} > {exc}\n")

        except Exception:
            print(
                f"{name} > Ocorreu um erro inesperado "
                "ao processar sua solicitação.\n"
            )