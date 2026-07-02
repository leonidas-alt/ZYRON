import requests


class OllamaClient:

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
