"""
ROADMAP DO MÓDULO

Versão Atual:

* Detecta wake word por correspondência textual simples.

Próxima Versão:

* Substituir por wake word acústica dedicada e limiares configuráveis.

Versão Futura:

* Wake word customizável por usuário e detecção sempre ativa otimizada.

Dependências Futuras:

* openWakeWord, Porcupine, modelos locais
"""

# TODO:
# Criar testes para variações de acento, pontuação, caixa e falsos positivos da wake word.
# FIXME:
# A detecção textual exige transcrição prévia e não funciona como wake word acústica real.
# IMPROVEMENT:
# Adicionar limiar de confiança, normalização fonética e configuração por usuário.
# FUTURE:
# Integrar openWakeWord ou Porcupine para escuta contínua eficiente e wake words customizadas.
# OPTIMIZATION:
# Detectar wake word antes de transcrever comandos longos para reduzir custo computacional.
# SECURITY:
# Adicionar modo privacidade para pausar a escuta e indicar visualmente quando o assistente está ativo.


"""Wake-word detection for ZYRON."""


class WakeWordDetector:
    """Detects and removes the configured activation word from transcripts."""

    def __init__(self, wake_word: str) -> None:
        """Normalize and store the wake word."""
        self.wake_word = wake_word.lower().strip()

    def is_wake_word_present(self, text: str) -> bool:
        """Return True when the activation word is present in the transcript."""
        return self.wake_word in text.lower()

    def remove_wake_word(self, text: str) -> str:
        """Remove the first wake-word occurrence and return the remaining command."""
        return text.lower().replace(self.wake_word, "", 1).strip(" ,.!?")
