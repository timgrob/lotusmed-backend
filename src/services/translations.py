import asyncio

from src.agents.agentic import Agentic, AIProvider
from src.core.exceptions import ProviderNotConfiguredError
from src.prompts import DocumentType, load_prompt
from src.schemas.paraphrase import (
    ParaphraseRequest,
    ParaphraseMultipleRequest,
    ProviderResult,
)
from src.schemas.provider import Provider


class TranslationService:
    def __init__(
        self,
        agents: dict[AIProvider, Agentic],
        default_models: dict[AIProvider, str],
    ) -> None:
        self._agents = agents
        self._default_models = default_models

    async def paraphrase(self, request: ParaphraseRequest) -> ProviderResult:
        provider = request.provider
        agent = self._agents.get(provider.name)
        if agent is None:
            raise ProviderNotConfiguredError(
                f"Provider is not configured: {provider.name}"
            )

        instructions = self._build_instructions(
            request.target_language, request.instructions
        )

        try:
            text = await agent.generate(instructions, request.text, provider.model)
            res = ProviderResult(text=text, provider=provider)
        except Exception as exc:
            res = ProviderResult(provider=provider, error=f"Error: {exc}")

        return res

    async def paraphrase_all(
        self, request: ParaphraseMultipleRequest
    ) -> list[ProviderResult]:
        targets = request.targets or self._default_targets()
        instructions = self._build_instructions(
            request.target_language, request.instructions
        )

        async def run_one(target: Provider) -> ProviderResult:
            agent = self._agents.get(target.name)
            if agent is None:
                return ProviderResult(
                    provider=target, error="Provider is not configured"
                )
            try:
                text = await agent.generate(instructions, request.text, target.model)
                return ProviderResult(text=text, provider=target)
            except Exception as exc:
                return ProviderResult(provider=target, error=f"Error: {exc}")

        return list(await asyncio.gather(*(run_one(t) for t in targets)))

    def _default_targets(self) -> list[Provider]:
        """Every configured provider paired with its default model."""
        return [
            Provider(name=provider, model=self._default_models[provider])
            for provider in self._agents
        ]

    @staticmethod
    def _build_instructions(
        target_language: str | None, add_instruction: str | None
    ) -> str:
        language_instruction = (
            f"Write the final text in {target_language}."
            if target_language
            else "Write the final text in the same language as the source text."
        )
        additional_instructions = (
            "Additional translation rules from the application owner:\n"
            f"{add_instruction}"
            if add_instruction
            else ""
        )
        parts = (
            load_prompt(DocumentType.MEDICAL_TRANSLATION.filename),
            language_instruction,
            additional_instructions,
        )
        return "\n\n".join(filter(None, parts))
