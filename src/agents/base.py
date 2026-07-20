from typing import Literal, Protocol

AIProvider = Literal["openai", "anthropic", "gemini"]


class TextGenerator(Protocol):
    model: str

    async def generate(self, instructions: str, text: str) -> str: ...
