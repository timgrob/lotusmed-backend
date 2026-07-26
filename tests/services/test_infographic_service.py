import base64

import pytest

from src.agents.agentic import AIProvider
from src.core.exceptions import InfographicRenderError, ProviderNotConfiguredError
from src.schemas.infographic import InfographicMultipleRequest, InfographicRequest
from src.schemas.provider import Provider
from src.services.infographic import InfographicService
from tests.fakes import FakeAgent, FakeRenderer

pytestmark = pytest.mark.anyio

DEFAULT_MODELS = {
    AIProvider.OPENAI: "openai-default",
    AIProvider.ANTHROPIC: "anthropic-default",
    AIProvider.GEMINI: "gemini-default",
}


def make_service(
    renderer: FakeRenderer | None = None, **agents: FakeAgent
) -> InfographicService:
    registry = {AIProvider(name): agent for name, agent in agents.items()}
    return InfographicService(
        agents=registry,
        default_models=DEFAULT_MODELS,
        renderer=renderer or FakeRenderer(),
    )


def target(provider: AIProvider, model: str = "some-model") -> Provider:
    return Provider(name=provider, model=model)


async def test_generate_selects_requested_provider_and_model():
    renderer = FakeRenderer(image=b"the-image")
    openai = FakeAgent(provider=AIProvider.OPENAI, text="<html></html>")
    service = make_service(renderer, openai=openai)

    image, provider = await service.generate(
        InfographicRequest(text="Report.", provider=target(AIProvider.OPENAI, "gpt"))
    )

    assert image == b"the-image"
    assert provider == target(AIProvider.OPENAI, "gpt")
    assert openai.model_used == "gpt"
    assert renderer.html == "<html></html>"


async def test_generate_unconfigured_provider_raises():
    service = make_service(openai=FakeAgent(provider=AIProvider.OPENAI))

    with pytest.raises(ProviderNotConfiguredError):
        await service.generate(
            InfographicRequest(text="Report.", provider=target(AIProvider.ANTHROPIC))
        )


async def test_generate_strips_markdown_code_fence():
    renderer = FakeRenderer()
    fenced = "```html\n<html><body>Hi</body></html>\n```"
    service = make_service(
        renderer, openai=FakeAgent(provider=AIProvider.OPENAI, text=fenced)
    )

    await service.generate(
        InfographicRequest(text="Report.", provider=target(AIProvider.OPENAI))
    )

    assert renderer.html == "<html><body>Hi</body></html>"


async def test_generate_propagates_render_error():
    service = make_service(
        FakeRenderer(error=InfographicRenderError("boom")),
        openai=FakeAgent(provider=AIProvider.OPENAI, text="<html></html>"),
    )

    with pytest.raises(InfographicRenderError):
        await service.generate(
            InfographicRequest(text="Report.", provider=target(AIProvider.OPENAI))
        )


async def test_generate_all_empty_targets_falls_back_to_configured_defaults():
    service = make_service(
        FakeRenderer(image=b"img"),
        openai=FakeAgent(provider=AIProvider.OPENAI, text="<html>ok</html>"),
        gemini=FakeAgent(provider=AIProvider.GEMINI, text="<html>ok</html>"),
    )

    results = await service.generate_all(InfographicMultipleRequest(text="Report."))

    by_provider = {r.provider.name: r for r in results}
    assert set(by_provider) == {AIProvider.OPENAI, AIProvider.GEMINI}
    assert by_provider[AIProvider.OPENAI].provider.model == "openai-default"
    assert by_provider[AIProvider.OPENAI].image_base64 == base64.b64encode(
        b"img"
    ).decode("ascii")


async def test_generate_all_reports_partial_failures():
    service = make_service(
        FakeRenderer(image=b"img"),
        openai=FakeAgent(provider=AIProvider.OPENAI, text="<html>ok</html>"),
        anthropic=FakeAgent(
            provider=AIProvider.ANTHROPIC,
            error=InfographicRenderError("anthropic down"),
        ),
    )

    results = await service.generate_all(
        InfographicMultipleRequest(
            text="Report.",
            targets=[
                target(AIProvider.OPENAI),
                target(AIProvider.ANTHROPIC),
            ],
        )
    )

    by_provider = {r.provider.name: r for r in results}
    assert by_provider[AIProvider.OPENAI].image_base64 is not None
    assert by_provider[AIProvider.OPENAI].error is None
    assert by_provider[AIProvider.ANTHROPIC].image_base64 is None
    assert "anthropic down" in by_provider[AIProvider.ANTHROPIC].error
