from typing import Annotated

from fastapi import Depends

from src.agents.agentic import AIProvider, Agentic
from src.agents.anthropic_agent import AnthropicAgent
from src.agents.gemini_agent import GeminiAgent
from src.agents.openai_agent import OpenaiAgent
from src.api.dependencies import SettingsDep


def get_anthropic_agent(settings: SettingsDep) -> AnthropicAgent:
    return AnthropicAgent(
        api_key=settings.ANTHROPIC_API_KEY.get_secret_value(),
        model=settings.ANTHROPIC_MODEL,
    )


def get_gemini_agent(settings: SettingsDep) -> GeminiAgent:
    return GeminiAgent(
        api_key=settings.GEMINI_API_KEY.get_secret_value(), model=settings.GEMINI_MODEL
    )


def get_openai_agent(settings: SettingsDep) -> OpenaiAgent:
    return OpenaiAgent(
        api_key=settings.OPENAI_API_KEY.get_secret_value(), model=settings.OPENAI_MODEL
    )


async def get_all_agents(
    anthropic: Annotated[AnthropicAgent, Depends(get_anthropic_agent)],
    gemini: Annotated[GeminiAgent, Depends(get_gemini_agent)],
    openai: Annotated[OpenaiAgent, Depends(get_openai_agent)],
) -> dict[str, Agentic]:
    return {
        AIProvider.ANTHROPIC: anthropic,
        AIProvider.GEMINI: gemini,
        AIProvider.OPENAI: openai,
    }


AnthropicAgentDep = Annotated[AnthropicAgent, Depends(get_anthropic_agent)]
GeminiAgentDep = Annotated[GeminiAgent, Depends(get_gemini_agent)]
OpenaiAgenttDep = Annotated[OpenaiAgent, Depends(get_openai_agent)]
AllAgentsDep = Annotated[dict[str, Agentic], Depends(get_all_agents)]
