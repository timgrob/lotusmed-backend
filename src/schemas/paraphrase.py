from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints
from src.schemas.provider import Provider


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
    provider: Provider = Field(
        description="AI provider to use. If omitted, the default is used.",
    )


class ParaphraseMultipleRequest(BaseModel):
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
    targets: list[Provider] = Field(
        default_factory=list,
        description=(
            "(provider, model) targets to run. If omitted, every configured "
            "provider is run at its default model."
        ),
    )


class ProviderResult(BaseModel):
    text: str | None = None
    provider: Provider | None = None
    error: str | None = None
