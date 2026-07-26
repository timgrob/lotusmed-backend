from openai import AsyncOpenAI, OpenAIError

from src.agents.agentic import AIProvider
from src.core.exceptions import UpstreamAIError


class OpenaiAgent:
    def __init__(self, api_key: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key, timeout=60.0, max_retries=2)
        self.provider = AIProvider.OPENAI

    async def generate(self, instructions: str, text: str, model: str) -> str:
        try:
            response = await self._client.responses.create(
                model=model,
                instructions=instructions,
                input=text,
            )
        except OpenAIError as exc:
            raise UpstreamAIError("Failed to generate text with OpenAI") from exc

        if not response.output_text:
            raise UpstreamAIError("OpenAI did not return any text")

        return response.output_text
