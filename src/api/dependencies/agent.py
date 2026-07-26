from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.agents.agentic import Agentic, AIProvider
from src.agents.anthropic_agent import AnthropicAgent
from src.agents.gemini_agent import GeminiAgent
from src.agents.openai_agent import OpenaiAgent
from src.core.config import get_settings


@lru_cache
def _build_agents() -> dict[AIProvider, Agentic]:
    """Construct one agent per configured provider, once per process."""
    settings = get_settings()
    agents: dict[AIProvider, Agentic] = {}

    if settings.ANTHROPIC_API_KEY is not None:
        agents[AIProvider.ANTHROPIC] = AnthropicAgent(
            api_key=settings.ANTHROPIC_API_KEY.get_secret_value()
        )
    if settings.GEMINI_API_KEY is not None:
        agents[AIProvider.GEMINI] = GeminiAgent(
            api_key=settings.GEMINI_API_KEY.get_secret_value()
        )
    if settings.OPENAI_API_KEY is not None:
        agents[AIProvider.OPENAI] = OpenaiAgent(
            api_key=settings.OPENAI_API_KEY.get_secret_value()
        )
    return agents


def get_agents() -> dict[AIProvider, Agentic]:
    return _build_agents()


AllAgentsDep = Annotated[dict[AIProvider, Agentic], Depends(get_agents)]
