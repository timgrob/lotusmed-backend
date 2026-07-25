import base64

import pytest

from src.agents.agentic import AIProvider
from src.core.exceptions import InfographicRenderError, ProviderNotConfiguredError
from src.schemas.infographic import InfographicRequest
from src.services.infographic import InfographicService
from tests.fakes import FakeAgent, FakeRenderer

pytestmark = pytest.mark.anyio


def make_service(
    renderer: FakeRenderer | None = None, **agents: FakeAgent
) -> InfographicService:
    registry = {AIProvider(name): agent for name, agent in agents.items()}
    return InfographicService(
        agents=registry,
        default_provider=AIProvider.OPENAI,
        renderer=renderer or FakeRenderer(),
    )


async def test_generate_uses_default_provider():
    renderer = FakeRenderer(image=b"the-image")
    service = make_service(
        renderer,
        openai=FakeAgent(provider=AIProvider.OPENAI, model="gpt", text="<html></html>"),
    )

    image, provider, model = await service.generate(InfographicRequest(text="Report."))

    assert image == b"the-image"
    assert provider == AIProvider.OPENAI
    assert model == "gpt"
    assert renderer.html == "<html></html>"


async def test_generate_selects_requested_provider():
    service = make_service(
        openai=FakeAgent(provider=AIProvider.OPENAI, text="<html>openai</html>"),
        gemini=FakeAgent(provider=AIProvider.GEMINI, text="<html>gemini</html>"),
    )

    _, provider, _ = await service.generate(
        InfographicRequest(text="Report.", provider=AIProvider.GEMINI)
    )

    assert provider == AIProvider.GEMINI


async def test_generate_unconfigured_provider_raises():
    service = make_service(openai=FakeAgent(provider=AIProvider.OPENAI))

    with pytest.raises(ProviderNotConfiguredError):
        await service.generate(
            InfographicRequest(text="Report.", provider=AIProvider.ANTHROPIC)
        )


async def test_generate_strips_markdown_code_fence():
    renderer = FakeRenderer()
    fenced = "```html\n<html><body>Hi</body></html>\n```"
    service = make_service(
        renderer, openai=FakeAgent(provider=AIProvider.OPENAI, text=fenced)
    )

    await service.generate(InfographicRequest(text="Report."))

    assert renderer.html == "<html><body>Hi</body></html>"


async def test_generate_propagates_render_error():
    service = make_service(
        FakeRenderer(error=InfographicRenderError("boom")),
        openai=FakeAgent(provider=AIProvider.OPENAI, text="<html></html>"),
    )

    with pytest.raises(InfographicRenderError):
        await service.generate(InfographicRequest(text="Report."))


async def test_generate_all_reports_partial_failures():
    service = make_service(
        FakeRenderer(image=b"img"),
        openai=FakeAgent(provider=AIProvider.OPENAI, text="<html>ok</html>"),
        anthropic=FakeAgent(
            provider=AIProvider.ANTHROPIC,
            error=InfographicRenderError("anthropic down"),
        ),
        gemini=FakeAgent(provider=AIProvider.GEMINI, text="<html>ok</html>"),
    )

    results = await service.generate_all(InfographicRequest(text="Report."))

    by_provider = {r.provider: r for r in results}
    assert len(results) == 3
    assert by_provider[AIProvider.OPENAI].image_base64 == base64.b64encode(
        b"img"
    ).decode("ascii")
    assert by_provider[AIProvider.OPENAI].error is None
    assert by_provider[AIProvider.GEMINI].image_base64 is not None
    assert by_provider[AIProvider.ANTHROPIC].image_base64 is None
    assert "anthropic down" in by_provider[AIProvider.ANTHROPIC].error
