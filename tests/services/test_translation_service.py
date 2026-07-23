import pytest

from src.agents.agentic import AIProvider
from src.core.exceptions import ProviderNotConfiguredError, UpstreamAIError
from src.schemas.paraphrase import ParaphraseRequest
from src.services.translations import TranslationService
from tests.fakes import FakeAgent

pytestmark = pytest.mark.anyio


def make_service(**agents: FakeAgent) -> TranslationService:
    registry = {AIProvider(name): agent for name, agent in agents.items()}
    return TranslationService(agents=registry, default_provider=AIProvider.OPENAI)


async def test_paraphrase_uses_default_provider():
    service = make_service(
        openai=FakeAgent(provider=AIProvider.OPENAI, model="gpt", text="Simple.")
    )

    result = await service.paraphrase(ParaphraseRequest(text="Complex."))

    assert result.text == "Simple."
    assert result.provider == AIProvider.OPENAI
    assert result.model == "gpt"


async def test_paraphrase_selects_requested_provider():
    service = make_service(
        openai=FakeAgent(provider=AIProvider.OPENAI, text="from-openai"),
        gemini=FakeAgent(provider=AIProvider.GEMINI, text="from-gemini"),
    )

    result = await service.paraphrase(
        ParaphraseRequest(text="Complex.", provider=AIProvider.GEMINI)
    )

    assert result.text == "from-gemini"
    assert result.provider == AIProvider.GEMINI


async def test_paraphrase_unconfigured_provider_raises():
    service = make_service(openai=FakeAgent(provider=AIProvider.OPENAI))

    with pytest.raises(ProviderNotConfiguredError):
        await service.paraphrase(
            ParaphraseRequest(text="Complex.", provider=AIProvider.ANTHROPIC)
        )


async def test_paraphrase_propagates_upstream_error():
    service = make_service(
        openai=FakeAgent(provider=AIProvider.OPENAI, error=UpstreamAIError("boom"))
    )

    with pytest.raises(UpstreamAIError):
        await service.paraphrase(ParaphraseRequest(text="Complex."))


async def test_paraphrase_all_reports_partial_failures():
    service = make_service(
        openai=FakeAgent(provider=AIProvider.OPENAI, text="ok-openai"),
        anthropic=FakeAgent(
            provider=AIProvider.ANTHROPIC, error=UpstreamAIError("anthropic down")
        ),
        gemini=FakeAgent(provider=AIProvider.GEMINI, text="ok-gemini"),
    )

    results = await service.paraphrase_all(ParaphraseRequest(text="Complex."))

    by_provider = {r.provider: r for r in results}
    assert len(results) == 3
    assert by_provider[AIProvider.OPENAI].text == "ok-openai"
    assert by_provider[AIProvider.OPENAI].error is None
    assert by_provider[AIProvider.GEMINI].text == "ok-gemini"
    assert by_provider[AIProvider.ANTHROPIC].text is None
    assert "anthropic down" in by_provider[AIProvider.ANTHROPIC].error
