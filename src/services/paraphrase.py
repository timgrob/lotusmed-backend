import asyncio

from src.agents.base import TextGenerator
from src.core.exceptions import ProviderNotConfiguredError
from src.prompts import load_prompt
from src.schemas.paraphrase import (
    ParaphraseComparisonResponse,
    ParaphraseRequest,
    ParaphraseResponse,
    ProviderResult,
)


class ParaphraseService:
    def __init__(
        self, providers: dict[str, TextGenerator], default_provider: str
    ) -> None:
        self._providers = providers
        self._default_provider = default_provider

    async def paraphrase(self, request: ParaphraseRequest) -> ParaphraseResponse:
        name = request.provider or self._default_provider
        generator = self._providers.get(name)
        if generator is None:
            raise ProviderNotConfiguredError(f"Provider is not configured: {name}")

        text = await generator.generate(self._build_instructions(request), request.text)
        return ParaphraseResponse(text=text, provider=name, model=generator.model)

    async def paraphrase_all(
        self, request: ParaphraseRequest
    ) -> ParaphraseComparisonResponse:
        instructions = self._build_instructions(request)
        names = list(self._providers)
        outcomes = await asyncio.gather(
            *(
                self._providers[name].generate(instructions, request.text)
                for name in names
            ),
            return_exceptions=True,
        )
        results = [
            ProviderResult(
                provider=name, model=self._providers[name].model, error=str(outcome)
            )
            if isinstance(outcome, BaseException)
            else ProviderResult(
                provider=name, model=self._providers[name].model, text=outcome
            )
            for name, outcome in zip(names, outcomes, strict=True)
        ]
        return ParaphraseComparisonResponse(results=results)

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
