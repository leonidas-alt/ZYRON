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
