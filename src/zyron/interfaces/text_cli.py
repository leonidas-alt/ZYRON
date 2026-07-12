from __future__ import annotations

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

    print(f"{name} online. Em que posso te ajudar?")
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