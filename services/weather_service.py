"""
ROADMAP DO MÓDULO

Versão Atual:

* Consulta temperatura atual pela OpenWeather API.

Próxima Versão:

* Adicionar cache, tratamento de erro e previsão detalhada.

Versão Futura:

* Alertas climáticos, automações por clima e múltiplas cidades.

Dependências Futuras:

* OpenWeather API, cache SQLite/Redis
"""

# TODO:
# Criar testes com mock HTTP para sucesso, cidade inválida, API key ausente, timeout e limite de requisições.
# FIXME:
# Falhas de rede ou respostas inesperadas ainda podem propagar exceções ao loop principal.
# IMPROVEMENT:
# Adicionar cache em SQLite, retries, descrição climática, umidade, sensação térmica e múltiplas cidades.
# FUTURE:
# Criar alertas climáticos, automações por clima e integração com dashboard web.
# OPTIMIZATION:
# Cachear respostas por janela de tempo para reduzir latência e consumo da OpenWeather API.
# SECURITY:
# Manter OPENWEATHER_API_KEY fora de logs e validar parâmetros enviados para a API externa.


"""Weather service backed by OpenWeather API."""

import requests


class WeatherService:
    """Fetches current weather information for the configured city."""

    def __init__(self, api_key: str, city: str) -> None:
        """Store OpenWeather credentials and location."""
        self.api_key = api_key
        self.city = city

    def current_temperature_text(self) -> str:
        """Return current temperature text, or a fallback when unavailable."""
        if not self.api_key:
            return "indisponível"
        params = {"q": self.city, "appid": self.api_key, "units": "metric", "lang": "pt_br"}
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=15)
        response.raise_for_status()
        temp = round(response.json()["main"]["temp"])
        return f"{temp} graus"
