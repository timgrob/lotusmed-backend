import logging

from openai import AsyncOpenAI, OpenAIError

from src.core.exceptions import UpstreamAIError
from src.prompts import load_prompt
from src.schemas.paraphrase import ParaphraseRequest

logger = logging.getLogger(__name__)


class ParaphraseService:
    def __init__(self, client: AsyncOpenAI, model: str) -> None:
        self._client = client
        self._model = model

    async def paraphrase(self, request: ParaphraseRequest) -> str:
        try:
            response = await self._client.responses.create(
                model=self._model,
                instructions=self._build_instructions(request),
                input=request.text,
            )
        except OpenAIError as exc:
            logger.exception("OpenAI paraphrase request failed")
            raise UpstreamAIError("Failed to generate paraphrased text") from exc

        if not response.output_text:
            logger.error("OpenAI returned an empty paraphrase response")
            raise UpstreamAIError("OpenAI did not return paraphrased text")
        return response.output_text

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
