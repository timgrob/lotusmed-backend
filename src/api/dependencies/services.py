from typing import Annotated

from fastapi import Depends

from src.agents import anthropic_agent, gemini_agent
from src.agents.anthropic_agent import AnthropicGenerator
from src.agents.base import TextGenerator
from src.agents.gemini_agent import GeminiGenerator
from src.agents.openai_agent import OpenAIGenerator
from src.api.dependencies.agent import AgentDep
from src.core.config import get_settings
from src.services.paraphrase import ParaphraseService


def get_paraphrase_service(agent: AgentDep) -> ParaphraseService:
    settings = get_settings()
    providers: dict[str, TextGenerator] = {
        "openai": OpenAIGenerator(client=agent, model=settings.OPENAI_MODEL_VERSION)
    }
    if anthropic_agent.client is not None:
        providers["anthropic"] = AnthropicGenerator(
            client=anthropic_agent.client, model=settings.ANTHROPIC_MODEL_VERSION
        )
    if gemini_agent.client is not None:
        providers["gemini"] = GeminiGenerator(
            client=gemini_agent.client, model=settings.GEMINI_MODEL_VERSION
        )
    return ParaphraseService(
        providers=providers, default_provider=settings.DEFAULT_AI_PROVIDER
    )


ParaphraseServiceDep = Annotated[ParaphraseService, Depends(get_paraphrase_service)]
