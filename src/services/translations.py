import asyncio

from src.agents.agentic import Agentic, AIProvider
from src.core.exceptions import ProviderNotConfiguredError
from src.prompts import load_prompt
from src.schemas.paraphrase import (
    ParaphraseRequest,
    ProviderResult,
)


class TranslationService:
    def __init__(self, agents: dict[str, Agentic]) -> None:
        self._agents: dict[str, Agentic] = agents

    async def paraphrase(self, request: ParaphraseRequest) -> ProviderResult:
        provider_name = request.provider if request.provider else AIProvider.OPENAI

        try:
            agent = self._agents.get(provider_name)
        except Exception as exc:
            raise ProviderNotConfiguredError(
                "Agent provider is not configured"
            ) from exc

        agent = self._agents.get(provider_name)
        if agent is None:
            raise ProviderNotConfiguredError("Agent provider is not configured")

        try:
            text = await agent.generate(self._build_instructions(request), request.text)
            return ProviderResult(text=text, provider=agent.provider, model=agent.model)
        except Exception as exc:
            return ProviderResult(
                text="", provider=agent.provider, model=agent.model, error=str(exc)
            )

    async def paraphrase_all(self, request: ParaphraseRequest) -> list[ProviderResult]:
        instructions = self._build_instructions(request)
        outcomes = await asyncio.gather(
            *(
                self._agents[provider].generate(instructions, request.text)
                for provider in AIProvider
            ),
            return_exceptions=True,
        )
        return [
            ProviderResult(
                text="",
                provider=provider,
                model=self._agents[provider].model,
                error=str(outcome),
            )
            if isinstance(outcome, BaseException)
            else ProviderResult(
                provider=provider, model=self._agents[provider].model, text=outcome
            )
            for provider, outcome in zip(AIProvider, outcomes, strict=True)
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
            load_prompt("medical_translation.md"),
            language_instruction,
            project_instructions,
        )
        return "\n\n".join(filter(None, parts))
