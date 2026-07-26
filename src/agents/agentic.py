from enum import StrEnum
from typing import Protocol


class AIProvider(StrEnum):
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENAI = "openai"


class Agentic(Protocol):
    provider: AIProvider

    async def generate(self, instructions: str, text: str, model: str) -> str: ...
