from commands.command_interpreter import CommandInterpreter
from core.models import CommandType

def test_interprets_google_search() -> None:
    intent = CommandInterpreter().interpret("pesquisar python 3.12")
    assert intent.command_type == CommandType.GOOGLE_SEARCH
    assert intent.target == "python 3.12"
