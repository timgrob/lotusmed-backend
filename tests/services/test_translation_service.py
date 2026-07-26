import pytest

from src.agents.agentic import AIProvider
from src.core.exceptions import ProviderNotConfiguredError
from src.schemas.paraphrase import ParaphraseMultipleRequest, ParaphraseRequest
from src.schemas.provider import Provider
from src.services.translations import TranslationService
from tests.fakes import FakeAgent

pytestmark = pytest.mark.anyio

DEFAULT_MODELS = {
    AIProvider.OPENAI: "openai-default",
    AIProvider.ANTHROPIC: "anthropic-default",
    AIProvider.GEMINI: "gemini-default",
}


def make_service(**agents: FakeAgent) -> TranslationService:
    registry = {AIProvider(name): agent for name, agent in agents.items()}
    return TranslationService(agents=registry, default_models=DEFAULT_MODELS)


def target(provider: AIProvider, model: str = "some-model") -> Provider:
    return Provider(name=provider, model=model)


async def test_paraphrase_selects_requested_provider_and_model():
    openai = FakeAgent(provider=AIProvider.OPENAI, text="from-openai")
    service = make_service(
        openai=openai,
        gemini=FakeAgent(provider=AIProvider.GEMINI, text="from-gemini"),
    )

    result = await service.paraphrase(
        ParaphraseRequest(text="Complex.", provider=target(AIProvider.OPENAI, "gpt"))
    )

    assert result.text == "from-openai"
    assert result.provider == target(AIProvider.OPENAI, "gpt")
    assert openai.model_used == "gpt"


async def test_paraphrase_unconfigured_provider_raises():
    service = make_service(openai=FakeAgent(provider=AIProvider.OPENAI))

    with pytest.raises(ProviderNotConfiguredError):
        await service.paraphrase(
            ParaphraseRequest(text="Complex.", provider=target(AIProvider.ANTHROPIC))
        )


async def test_paraphrase_captures_upstream_error():
    service = make_service(
        openai=FakeAgent(provider=AIProvider.OPENAI, error=RuntimeError("boom"))
    )

    result = await service.paraphrase(
        ParaphraseRequest(text="Complex.", provider=target(AIProvider.OPENAI))
    )

    assert result.text is None
    assert "boom" in result.error


async def test_paraphrase_all_runs_explicit_targets():
    openai = FakeAgent(provider=AIProvider.OPENAI, text="ok")
    service = make_service(openai=openai)

    results = await service.paraphrase_all(
        ParaphraseMultipleRequest(
            text="Complex.",
            targets=[
                target(AIProvider.OPENAI, "gpt-5.5"),
                target(AIProvider.OPENAI, "gpt-4o"),
            ],
        )
    )

    assert [r.provider.model for r in results] == ["gpt-5.5", "gpt-4o"]
    assert all(r.text == "ok" for r in results)


async def test_paraphrase_all_empty_targets_falls_back_to_configured_defaults():
    service = make_service(
        openai=FakeAgent(provider=AIProvider.OPENAI, text="ok-openai"),
        gemini=FakeAgent(provider=AIProvider.GEMINI, text="ok-gemini"),
    )

    results = await service.paraphrase_all(ParaphraseMultipleRequest(text="Complex."))

    by_provider = {r.provider.name: r for r in results}
    assert set(by_provider) == {AIProvider.OPENAI, AIProvider.GEMINI}
    assert by_provider[AIProvider.OPENAI].provider.model == "openai-default"
    assert by_provider[AIProvider.GEMINI].provider.model == "gemini-default"


async def test_paraphrase_all_reports_partial_failures():
    service = make_service(
        openai=FakeAgent(provider=AIProvider.OPENAI, text="ok-openai"),
        anthropic=FakeAgent(
            provider=AIProvider.ANTHROPIC, error=RuntimeError("anthropic down")
        ),
        gemini=FakeAgent(provider=AIProvider.GEMINI, text="ok-gemini"),
    )

    results = await service.paraphrase_all(
        ParaphraseMultipleRequest(
            text="Complex.",
            targets=[
                target(AIProvider.OPENAI),
                target(AIProvider.ANTHROPIC),
                target(AIProvider.GEMINI),
                target(AIProvider.OPENAI, "unconfigured-name-still-openai"),
            ],
        )
    )

    by_provider = {r.provider.name: r for r in results if r.error is None}
    assert by_provider[AIProvider.OPENAI].text == "ok-openai"
    assert by_provider[AIProvider.GEMINI].text == "ok-gemini"
    anthropic_result = next(r for r in results if r.provider.name == AIProvider.ANTHROPIC)
    assert anthropic_result.text is None
    assert "anthropic down" in anthropic_result.error


async def test_paraphrase_all_unconfigured_target_becomes_error_item():
    service = make_service(openai=FakeAgent(provider=AIProvider.OPENAI, text="ok"))

    results = await service.paraphrase_all(
        ParaphraseMultipleRequest(
            text="Complex.", targets=[target(AIProvider.ANTHROPIC)]
        )
    )

    assert len(results) == 1
    assert results[0].text is None
    assert "not configured" in results[0].error
