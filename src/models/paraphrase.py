from typing import Literal

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


class MedicalImageRequest(BaseModel):
    text: str = Field(..., min_length=1)
    instructions: str | None = Field(
        default=None,
        description="Optional project-specific medical depiction rules.",
    )
    size: Literal["auto", "1024x1024", "1536x1024", "1024x1536", "2048x2048", "2048x1152"] = "auto"
    quality: Literal["auto", "low", "medium", "high"] = "auto"
    output_format: Literal["png", "jpeg", "webp"] = "png"
    output_compression: int = Field(default=0, ge=0, le=100, description="Image compression")


class MedicalImageResponse(BaseModel):
    image: str
    mime_type: Literal["image/png"] = "image/png"
