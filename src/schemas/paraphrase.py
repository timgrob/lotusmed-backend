from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from src.agents.agentic import AIProviderName


class ParaphraseRequest(BaseModel):
    text: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000)
    ]
    instructions: (
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=5_000)]
        | None
    ) = Field(
        default=None,
        description="Optional project-specific translation/paraphrasing rules.",
    )
    target_language: str | None = Field(
        default=None,
        description="Optional output language. If omitted, the source language is preserved.",
    )
    provider: AIProviderName | None = Field(
        default=None,
        description="AI provider to use. If omitted, the server default is used.",
    )


class ParaphraseResponse(BaseModel):
    text: str
    provider: str
    model: str


class ProviderResult(BaseModel):
    text: str
    provider: str
    model: str
    error: str | None = None
