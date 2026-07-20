from google import genai
from google.genai import types
from google.genai.errors import APIError

from src.core.config import get_settings
from src.core.exceptions import UpstreamAIError

settings = get_settings()

client = (
    genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())
    if settings.GEMINI_API_KEY
    else None
)


class GeminiGenerator:
    def __init__(self, client: genai.Client, model: str) -> None:
        self._client = client
        self.model = model

    async def generate(self, instructions: str, text: str) -> str:
        try:
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=text,
                config=types.GenerateContentConfig(system_instruction=instructions),
            )
        except APIError as exc:
            raise UpstreamAIError("Failed to generate text with Gemini") from exc

        output = response.text or ""
        if not output:
            raise UpstreamAIError("Gemini did not return any text")
        return output
