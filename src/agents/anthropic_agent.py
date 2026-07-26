from anthropic import APIError, AsyncAnthropic

from src.agents.agentic import AIProvider
from src.core.exceptions import UpstreamAIError


class AnthropicAgent:
    def __init__(self, api_key: str) -> None:
        self._client = AsyncAnthropic(api_key=api_key, timeout=60.0, max_retries=2)
        self.provider: AIProvider = AIProvider.ANTHROPIC

    async def generate(self, instructions: str, text: str, model: str) -> str:
        try:
            response = await self._client.messages.create(
                model=model,
                max_tokens=16_000,
                system=instructions,
                messages=[{"role": "user", "content": text}],
            )
        except APIError as exc:
            raise UpstreamAIError(
                f"Failed to generate text with Anthropic: {exc}"
            ) from exc

        if response.stop_reason == "refusal":
            raise UpstreamAIError("Anthropic declined to generate text")

        output = next(
            (block.text for block in response.content if block.type == "text"), ""
        )
        if not output:
            raise UpstreamAIError("Anthropic did not return any text")
        return output
