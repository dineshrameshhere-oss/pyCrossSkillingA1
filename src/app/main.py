from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import httpx
from anthropic import AsyncAnthropic
from fastapi import FastAPI

from app.config import get_settings
from app.routers import external, summary


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    timeout = httpx.Timeout(settings.http_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as http_client:
        app.state.http_client = http_client
        app.state.llm_client = AsyncAnthropic(
            api_key=settings.anthropic_api_key.get_secret_value(),
            timeout=settings.http_timeout_seconds,
        )
        try:
            yield
        finally:
            await app.state.llm_client.close()


app = FastAPI(
    title="Utility and Summary API",
    description="Current weather, a random joke, and authenticated text summaries.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(external.router)
app.include_router(summary.router)
