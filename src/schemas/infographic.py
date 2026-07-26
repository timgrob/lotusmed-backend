from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from src.schemas.provider import Provider


class InfographicRequest(BaseModel):
    text: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000)
    ]
    instructions: (
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=5_000)]
        | None
    ) = Field(
        default=None,
        description="Optional project-specific infographic rules.",
    )
    provider: Provider = Field(
        default_factory=Provider,
        description="(provider, model) target to render the infographic with.",
    )


class InfographicMultipleRequest(BaseModel):
    text: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000)
    ]
    instructions: (
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=5_000)]
        | None
    ) = Field(
        default=None,
        description="Optional project-specific infographic rules.",
    )
    targets: list[Provider] = Field(
        default_factory=list,
        description=(
            "(provider, model) targets to run. If omitted, every configured "
            "provider is run at its default model."
        ),
    )


class InfographicProviderResult(BaseModel):
    image_base64: str | None = None
    provider: Provider | None = None
    error: str | None = None
