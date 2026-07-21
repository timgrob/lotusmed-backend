from enum import StrEnum
from typing import Literal, Protocol

AIProviderName = Literal["openai", "anthropic", "gemini"]


class AIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENAI = "openai"


class Agentic(Protocol):
    model: str
    provider: AIProvider

    async def generate(self, instructions: str, text: str) -> str: ...
