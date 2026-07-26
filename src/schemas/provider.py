from pydantic import BaseModel, Field

from src.agents.agentic import AIProvider


class Provider(BaseModel):
    name: AIProvider = Field(
        default=AIProvider.ANTHROPIC,
        description="Optional AI provider. If omitted, the server default is used.",
    )
    model: str = Field(
        default="claude-opus-4-8",
        description="Optional model version. If omitted, the server default is used.",
    )
