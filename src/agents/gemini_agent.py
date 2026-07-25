from google import genai
from google.genai import types
from google.genai.errors import APIError

from src.agents.agentic import AIProvider
from src.core.exceptions import UpstreamAIError


class GeminiAgent:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self.model: str = model
        self.provider: AIProvider = AIProvider.GEMINI

    async def generate(self, instructions: str, text: str) -> str:
        try:
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=text,
                config=types.GenerateContentConfig(system_instruction=instructions),
            )
        except APIError as exc:
            raise UpstreamAIError(
                f"Failed to generate text with Gemini: {exc}"
            ) from exc

        output = response.text or ""
        if not output:
            raise UpstreamAIError("Gemini did not return any text")

        return output
