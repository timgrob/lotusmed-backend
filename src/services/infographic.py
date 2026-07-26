import asyncio
import base64

from src.agents.agentic import Agentic, AIProvider
from src.core.exceptions import ProviderNotConfiguredError
from src.prompts import DocumentType, load_prompt
from src.schemas.infographic import (
    InfographicMultipleRequest,
    InfographicProviderResult,
    InfographicRequest,
)
from src.schemas.provider import Provider
from src.services.html_renderer import Renderer

_HTML_OUTPUT_INSTRUCTION = (
    "Output ONLY one complete, self-contained HTML document and nothing else. "
    "Do not wrap it in markdown code fences. Inline all CSS in a <style> tag; "
    "do not reference any external resources (fonts, images, scripts, or "
    "stylesheets). Design for a single-column mobile layout about 420 pixels "
    "wide."
)


class InfographicService:
    def __init__(
        self,
        agents: dict[AIProvider, Agentic],
        default_models: dict[AIProvider, str],
        renderer: Renderer,
    ) -> None:
        self._agents = agents
        self._default_models = default_models
        self._renderer = renderer

    async def generate(self, request: InfographicRequest) -> tuple[bytes, Provider]:
        provider = request.provider
        agent = self._agents.get(provider.name)
        if agent is None:
            raise ProviderNotConfiguredError(
                f"Provider is not configured: {provider.name}"
            )

        instructions = self._build_instructions(request.instructions)
        image = await self._render_infographic(
            agent, instructions, request.text, provider.model
        )
        return image, provider

    async def generate_all(
        self, request: InfographicMultipleRequest
    ) -> list[InfographicProviderResult]:
        targets = request.targets or self._default_targets()
        instructions = self._build_instructions(request.instructions)

        async def run_one(target: Provider) -> InfographicProviderResult:
            agent = self._agents.get(target.name)
            if agent is None:
                return InfographicProviderResult(
                    provider=target, error="Provider is not configured"
                )
            try:
                image = await self._render_infographic(
                    agent, instructions, request.text, target.model
                )
                return InfographicProviderResult(
                    image_base64=base64.b64encode(image).decode("ascii"),
                    provider=target,
                )
            except Exception as exc:
                return InfographicProviderResult(
                    provider=target, error=f"Error: {exc}"
                )

        return list(await asyncio.gather(*(run_one(t) for t in targets)))

    def _default_targets(self) -> list[Provider]:
        """Every configured provider paired with its default model."""
        return [
            Provider(name=provider, model=self._default_models[provider])
            for provider in self._agents
        ]

    async def _render_infographic(
        self, agent: Agentic, instructions: str, text: str, model: str
    ) -> bytes:
        html = await agent.generate(instructions, text, model)
        return await self._renderer.render(self._strip_code_fence(html))

    @staticmethod
    def _build_instructions(instructions: str | None) -> str:
        project_instructions = (
            "Additional infographic rules from the application owner:\n"
            f"{instructions}"
            if instructions
            else ""
        )
        parts = (
            load_prompt(DocumentType.MEDICAL_INFOGRAPHIC.filename),
            _HTML_OUTPUT_INSTRUCTION,
            project_instructions,
        )
        return "\n\n".join(filter(None, parts))

    @staticmethod
    def _strip_code_fence(html: str) -> str:
        """Remove a surrounding markdown code fence if the model added one."""
        stripped = html.strip()
        if not stripped.startswith("```"):
            return stripped
        lines = stripped.splitlines()
        # Drop the opening fence line (e.g. ``` or ```html) and any closing fence.
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
