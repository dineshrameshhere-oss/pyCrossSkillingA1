from anthropic import APIError, AsyncAnthropic


class SummaryProviderError(Exception):
    """Raised when the LLM provider fails to generate a summary."""


class SummaryService:
    SYSTEM_PROMPT = (
        "Summarize the user's text accurately in 3-5 concise sentences. "
        "Preserve the main claims and important caveats. Do not add facts."
    )

    def __init__(self, client: AsyncAnthropic, model: str) -> None:
        self._client = client
        self._model = model

    async def summarize(self, text: str) -> str:
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=400,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text}],
            )
            summary = "".join(
                block.text for block in response.content if block.type == "text"
            )
            if not summary.strip():
                raise SummaryProviderError("Empty summary response")
            return summary.strip()
        except APIError as exc:
            raise SummaryProviderError from exc
