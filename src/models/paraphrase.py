from pydantic import BaseModel, Field


class ParaphraseRequest(BaseModel):
    text: str = Field(..., min_length=1)
    instructions: str | None = Field(
        default=None,
        description="Optional project-specific translation/paraphrasing rules.",
    )
    target_language: str | None = Field(
        default=None,
        description="Optional output language. If omitted, the source language is preserved.",
    )


class ParaphraseResponse(BaseModel):
    text: str
