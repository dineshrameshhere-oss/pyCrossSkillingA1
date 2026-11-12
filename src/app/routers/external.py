import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.schemas import JokeResponse, WeatherResponse
from app.services.jokes import JokeProviderError, JokeService
from app.services.weather import CityNotFoundError, WeatherProviderError, WeatherService

router = APIRouter(tags=["external APIs"])


def _http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    city: str = Query(min_length=1, max_length=120),
    client: httpx.AsyncClient = Depends(_http_client),
) -> WeatherResponse:
    try:
        data = await WeatherService(client).current(city.strip())
    except CityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found") from None
    except WeatherProviderError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Weather provider unavailable"
        ) from None
    return WeatherResponse(**data)


@router.get("/joke", response_model=JokeResponse)
async def get_joke(client: httpx.AsyncClient = Depends(_http_client)) -> JokeResponse:
    try:
        data = await JokeService(client).random()
    except JokeProviderError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Joke provider unavailable"
        ) from None
    return JokeResponse(**data)
