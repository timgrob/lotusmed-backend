from openai import AsyncOpenAI, OpenAIError

from src.core.config import get_settings
from src.core.exceptions import UpstreamAIError

settings = get_settings()

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    timeout=60.0,
    max_retries=2,
)


def get_agent() -> AsyncOpenAI:
    return client


class OpenAIGenerator:
    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        self._client = client
        self.model = model

    async def generate(self, instructions: str, text: str) -> str:
        try:
            response = await self._client.responses.create(
                model=self.model,
                instructions=instructions,
                input=text,
            )
        except OpenAIError as exc:
            raise UpstreamAIError("Failed to generate text with OpenAI") from exc

        if not response.output_text:
            raise UpstreamAIError("OpenAI did not return any text")
        return response.output_text
