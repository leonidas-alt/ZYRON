"""
ROADMAP DO MÓDULO

Versão Atual:

* Expõe entrada e saída de voz.

Próxima Versão:

* Padronizar engines de STT/TTS/wake word.

Versão Futura:

* Voz multimodal com biometria e streaming.

Dependências Futuras:

* Faster-Whisper, Edge-TTS, openWakeWord
"""

# TODO:
# Definir explicitamente exports públicos (__all__) quando o pacote ganhar mais módulos.
# FIXME:
# O pacote ainda não possui factories ou contratos formais para descoberta dinâmica.
# IMPROVEMENT:
# Documentar convenções internas para novos módulos e integrações.
# FUTURE:
# Preparar suporte a sistema de plugins, multiusuário, dashboard web, PostgreSQL, ChromaDB, Docker, Kubernetes e AWS conforme necessário.
# OPTIMIZATION:
# Evitar imports pesados no __init__ para manter inicialização rápida.
# SECURITY:
# Não expor objetos sensíveis ou clientes autenticados diretamente pelo pacote.


"""Voice input and output package for ZYRON."""
