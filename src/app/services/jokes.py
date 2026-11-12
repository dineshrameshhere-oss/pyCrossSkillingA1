import httpx


class JokeProviderError(Exception):
    """Raised when the joke provider is unavailable or returns invalid data."""


class JokeService:
    URL = "https://v2.jokeapi.dev/joke/Any?type=single"

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def random(self) -> dict[str, str]:
        try:
            response = await self._client.get(self.URL)
            response.raise_for_status()
            payload = response.json()
            if payload.get("error") or not payload.get("joke") or not payload.get("category"):
                raise ValueError("Invalid joke response")
            return {"joke": payload["joke"], "category": payload["category"]}
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            raise JokeProviderError from exc
