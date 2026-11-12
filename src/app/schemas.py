from pydantic import BaseModel, ConfigDict


class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int


class JokeResponse(BaseModel):
    joke: str
    category: str


class SummaryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str


class SummaryResponse(BaseModel):
    summary: str
