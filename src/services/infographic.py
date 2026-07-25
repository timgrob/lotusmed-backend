import asyncio
import base64

from src.agents.agentic import Agentic, AIProvider
from src.core.exceptions import ProviderNotConfiguredError
from src.prompts import DocumentType, load_prompt
from src.schemas.infographic import InfographicProviderResult, InfographicRequest
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
        default_provider: AIProvider,
        renderer: Renderer,
    ) -> None:
        self._agents = agents
        self._default_provider = default_provider
        self._renderer = renderer

    async def generate(
        self, request: InfographicRequest
    ) -> tuple[bytes, AIProvider, str]:
        provider = request.provider or self._default_provider
        agent = self._agents.get(provider)
        if agent is None:
            raise ProviderNotConfiguredError(f"Provider is not configured: {provider}")

        image = await self._render_infographic(agent, request)
        return image, agent.provider, agent.model

    async def generate_all(
        self, request: InfographicRequest
    ) -> list[InfographicProviderResult]:
        agents = list(self._agents.values())
        outcomes = await asyncio.gather(
            *(self._render_infographic(agent, request) for agent in agents),
            return_exceptions=True,
        )
        return [
            InfographicProviderResult(
                provider=agent.provider, model=agent.model, error=str(outcome)
            )
            if isinstance(outcome, BaseException)
            else InfographicProviderResult(
                image_base64=base64.b64encode(outcome).decode("ascii"),
                provider=agent.provider,
                model=agent.model,
            )
            for agent, outcome in zip(agents, outcomes, strict=True)
        ]

    async def _render_infographic(
        self, agent: Agentic, request: InfographicRequest
    ) -> bytes:
        html = await agent.generate(self._build_instructions(request), request.text)
        return await self._renderer.render(self._strip_code_fence(html))

    @staticmethod
    def _build_instructions(request: InfographicRequest) -> str:
        project_instructions = (
            "Additional infographic rules from the application owner:\n"
            f"{request.instructions}"
            if request.instructions
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
