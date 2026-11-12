import httpx


class CityNotFoundError(Exception):
    """Raised when geocoding cannot find a requested city."""


class WeatherProviderError(Exception):
    """Raised when the weather provider is unavailable or returns invalid data."""


class WeatherService:
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def current(self, city: str) -> dict[str, str | float | int]:
        try:
            location_response = await self._client.get(
                self.GEOCODING_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
            )
            location_response.raise_for_status()
            locations = location_response.json().get("results") or []
            if not locations:
                raise CityNotFoundError

            location = locations[0]
            weather_response = await self._client.get(
                self.FORECAST_URL,
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": "temperature_2m,relative_humidity_2m,weather_code",
                    "temperature_unit": "celsius",
                },
            )
            weather_response.raise_for_status()
            current = weather_response.json()["current"]
            return {
                "city": location["name"],
                "temperature": current["temperature_2m"],
                "condition": self._condition(current["weather_code"]),
                "humidity": current["relative_humidity_2m"],
            }
        except CityNotFoundError:
            raise
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise WeatherProviderError from exc

    @staticmethod
    def _condition(code: int) -> str:
        if code == 0:
            return "Clear sky"
        if code in (1, 2, 3):
            return "Mainly clear, partly cloudy, or overcast"
        if code in (45, 48):
            return "Fog"
        if code in (51, 53, 55, 56, 57):
            return "Drizzle"
        if code in (61, 63, 65, 66, 67):
            return "Rain"
        if code in (71, 73, 75, 77):
            return "Snow"
        if code in (80, 81, 82):
            return "Rain showers"
        if code in (85, 86):
            return "Snow showers"
        if code in (95, 96, 99):
            return "Thunderstorm"
        return "Unknown"
