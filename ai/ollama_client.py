"""
ROADMAP DO MÓDULO

Versão Atual:

* Comunica com Ollama local para geração de texto.

Próxima Versão:

* Adicionar prompt de sistema, retries, health checks e classificação de intents.

Versão Futura:

* Roteamento multimodelo, embeddings, memória vetorial e ferramentas.

Dependências Futuras:

* Ollama embeddings, ChromaDB, PostgreSQL/pgvector
"""

# TODO:
# Criar testes com servidor HTTP fake para respostas válidas, timeout, erro 500 e JSON inesperado.
# FIXME:
# O cliente ainda não possui retries, health check nem fallback quando o Ollama está offline.
# IMPROVEMENT:
# Adicionar prompts de sistema, classificação de intents em JSON e injeção de sessão HTTP testável.
# FUTURE:
# Integrar embeddings, ChromaDB, PostgreSQL/pgvector, memória vetorial e roteamento entre múltiplos modelos locais.
# OPTIMIZATION:
# Reutilizar conexões HTTP com requests.Session e cachear respostas determinísticas quando aplicável.
# SECURITY:
# Sanitizar contexto enviado ao modelo para evitar exposição de tokens, e-mails, finanças ou dados sensíveis.


"""Client for communicating with a local Ollama server."""

import requests


class OllamaClient:
    """Small HTTP client that sends prompts to Ollama and returns model responses."""

    def __init__(self, base_url: str, model: str, timeout: int = 120) -> None:
        """Store Ollama connection details."""
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        """Generate a response from the configured local model."""
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json().get("response", "")
