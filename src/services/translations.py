import asyncio

from src.agents.agentic import Agentic, AIProvider
from src.core.exceptions import ProviderNotConfiguredError
from src.prompts import DocumentType, load_prompt
from src.schemas.paraphrase import (
    ParaphraseRequest,
    ParaphraseResponse,
    ProviderResult,
)


class TranslationService:
    def __init__(
        self, agents: dict[AIProvider, Agentic], default_provider: AIProvider
    ) -> None:
        self._agents = agents
        self._default_provider = default_provider

    async def paraphrase(self, request: ParaphraseRequest) -> ParaphraseResponse:
        provider = request.provider or self._default_provider
        agent = self._agents.get(provider)
        if agent is None:
            raise ProviderNotConfiguredError(f"Provider is not configured: {provider}")

        text = await agent.generate(self._build_instructions(request), request.text)
        return ParaphraseResponse(text=text, provider=agent.provider, model=agent.model)

    async def paraphrase_all(self, request: ParaphraseRequest) -> list[ProviderResult]:
        instructions = self._build_instructions(request)
        agents = list(self._agents.values())
        outcomes = await asyncio.gather(
            *(agent.generate(instructions, request.text) for agent in agents),
            return_exceptions=True,
        )
        return [
            ProviderResult(
                provider=agent.provider, model=agent.model, error=str(outcome)
            )
            if isinstance(outcome, BaseException)
            else ProviderResult(
                text=outcome, provider=agent.provider, model=agent.model
            )
            for agent, outcome in zip(agents, outcomes, strict=True)
        ]

    @staticmethod
    def _build_instructions(request: ParaphraseRequest) -> str:
        language_instruction = (
            f"Write the final text in {request.target_language}."
            if request.target_language
            else "Write the final text in the same language as the source text."
        )
        project_instructions = (
            "Additional translation rules from the application owner:\n"
            f"{request.instructions}"
            if request.instructions
            else ""
        )
        parts = (
            load_prompt(DocumentType.MEDICAL_TRANSLATION.filename),
            language_instruction,
            project_instructions,
        )
        return "\n\n".join(filter(None, parts))
