import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from anthropic import AsyncAnthropic

from app.config import Settings, get_settings
from app.schemas import SummaryRequest, SummaryResponse
from app.services.summaries import SummaryProviderError, SummaryService

router = APIRouter(tags=["summaries"])


@router.post("/summary", response_model=SummaryResponse)
async def create_summary(
    body: SummaryRequest,
    request: Request,
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> SummaryResponse:
    if not x_api_key or not hmac.compare_digest(x_api_key, settings.api_key.get_secret_value()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    if not body.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text must not be empty")
    if len(body.text) > settings.summary_max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text must not exceed {settings.summary_max_length} characters",
        )

    client: AsyncAnthropic = request.app.state.llm_client
    try:
        result = await SummaryService(client, settings.anthropic_model).summarize(body.text)
    except SummaryProviderError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Summary provider unavailable"
        ) from None
    return SummaryResponse(summary=result)
