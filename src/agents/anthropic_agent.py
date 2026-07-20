from anthropic import APIError, AsyncAnthropic

from src.core.config import get_settings
from src.core.exceptions import UpstreamAIError

settings = get_settings()

client = (
    AsyncAnthropic(
        api_key=settings.ANTHROPIC_API_KEY.get_secret_value(),
        timeout=60.0,
        max_retries=2,
    )
    if settings.ANTHROPIC_API_KEY
    else None
)


class AnthropicGenerator:
    def __init__(self, client: AsyncAnthropic, model: str) -> None:
        self._client = client
        self.model = model

    async def generate(self, instructions: str, text: str) -> str:
        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=16_000,
                system=instructions,
                messages=[{"role": "user", "content": text}],
            )
        except APIError as exc:
            raise UpstreamAIError("Failed to generate text with Anthropic") from exc

        if response.stop_reason == "refusal":
            raise UpstreamAIError("Anthropic declined to generate text")

        output = next(
            (block.text for block in response.content if block.type == "text"), ""
        )
        if not output:
            raise UpstreamAIError("Anthropic did not return any text")
        return output
