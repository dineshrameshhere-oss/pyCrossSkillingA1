# Utility and Summary API

A small FastAPI microservice with weather and joke provider wrappers plus an API-key-protected LLM summary endpoint.

## Requirements

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/)
- An Anthropic API key

## Setup

```powershell
uv sync
Copy-Item .env.example .env
```

Set `API_KEY` to a long random secret and `ANTHROPIC_API_KEY` to your provider key in `.env`. The summary endpoint uses Anthropic's Messages API and defaults to `claude-haiku-4-5-20251001`. It asks for an accurate, concise summary in 3–5 sentences, preserving key claims and caveats without adding facts. Set `ANTHROPIC_MODEL` to another supported Claude model if desired. Input is limited to 20,000 characters by default (`SUMMARY_MAX_LENGTH`).

## Run

```powershell
uv run uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000
```

Interactive API docs are at `http://localhost:8000/docs`.

## Endpoints

### `GET /weather?city=London`

Returns current Celsius temperature, a human-readable condition, and relative humidity. Uses Open-Meteo geocoding and forecast APIs.

```json
{"city":"London","temperature":12.4,"condition":"Rain","humidity":81}
```

Returns `404` when geocoding finds no city and `502` when the weather provider fails or returns unusable data. Provider requests have a configurable timeout (`HTTP_TIMEOUT_SECONDS`, default 8 seconds).

### `GET /joke`

Returns a random single-part joke and its category from JokeAPI.

```json
{"joke":"Example joke text","category":"Pun"}
```

Returns `502` if the provider is unavailable.

### `POST /summary`

Requires `X-API-Key` matching `API_KEY`. The JSON body must contain non-empty `text` within the configured maximum length.

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/summary `
  -Headers @{'X-API-Key'='your-configured-key'} `
  -ContentType 'application/json' `
  -Body '{"text":"Text to summarize goes here."}'
```

Returns `401` for a missing or invalid key, `400` for text over the configured maximum, `422` for a missing or empty text field, and `502` if the LLM provider fails.

## Project structure

```text
src/app/
  config.py            # Environment-backed settings
  main.py              # App factory/lifespan and router registration
  schemas.py           # Request/response validation
  routers/             # HTTP endpoints and status mapping
  services/            # External provider integrations
```

Each provider client is shared through the application lifespan, uses bounded timeouts, and translates upstream failures into provider-specific exceptions before the route maps them to HTTP responses. Secrets are read from the environment and are never returned by the API.
