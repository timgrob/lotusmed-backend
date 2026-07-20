import pytest

from src.core.exceptions import ProviderNotConfiguredError, UpstreamAIError
from src.schemas.paraphrase import ParaphraseRequest
from src.services.paraphrase import ParaphraseService
from tests.fakes import FakeGenerator

pytestmark = pytest.mark.anyio

REQUEST = ParaphraseRequest(text="Myocardial infarction.")


async def test_paraphrase_uses_default_provider():
    openai = FakeGenerator(model="gpt-test", text="From OpenAI.")
    service = ParaphraseService(providers={"openai": openai}, default_provider="openai")

    response = await service.paraphrase(REQUEST)

    assert response.text == "From OpenAI."
    assert response.provider == "openai"
    assert response.model == "gpt-test"
    assert openai.input_text == "Myocardial infarction."


async def test_paraphrase_uses_requested_provider():
    openai = FakeGenerator(text="From OpenAI.")
    anthropic = FakeGenerator(model="claude-test", text="From Claude.")
    service = ParaphraseService(
        providers={"openai": openai, "anthropic": anthropic},
        default_provider="openai",
    )

    response = await service.paraphrase(
        ParaphraseRequest(text="Myocardial infarction.", provider="anthropic")
    )

    assert response.text == "From Claude."
    assert response.provider == "anthropic"
    assert response.model == "claude-test"
    assert openai.input_text is None


async def test_paraphrase_unconfigured_provider():
    service = ParaphraseService(
        providers={"openai": FakeGenerator()}, default_provider="openai"
    )

    with pytest.raises(ProviderNotConfiguredError):
        await service.paraphrase(
            ParaphraseRequest(text="Myocardial infarction.", provider="gemini")
        )


async def test_paraphrase_defaults_to_source_language():
    generator = FakeGenerator()
    service = ParaphraseService(
        providers={"openai": generator}, default_provider="openai"
    )

    await service.paraphrase(REQUEST)

    assert generator.instructions is not None
    assert (
        "Write the final text in the same language as the source text."
        in generator.instructions
    )
    assert not generator.instructions.endswith("\n")


async def test_paraphrase_includes_language_and_instructions():
    generator = FakeGenerator()
    service = ParaphraseService(
        providers={"openai": generator}, default_provider="openai"
    )

    await service.paraphrase(
        ParaphraseRequest(
            text="Myocardial infarction.",
            target_language="German",
            instructions="Use short sentences.",
        )
    )

    assert generator.instructions is not None
    assert "Write the final text in German." in generator.instructions
    assert (
        "Additional translation rules from the application owner:\nUse short sentences."
        in generator.instructions
    )


async def test_paraphrase_all_collects_results():
    service = ParaphraseService(
        providers={
            "openai": FakeGenerator(model="gpt-test", text="From OpenAI."),
            "anthropic": FakeGenerator(
                model="claude-test", error=UpstreamAIError("upstream failure")
            ),
        },
        default_provider="openai",
    )

    comparison = await service.paraphrase_all(REQUEST)

    results = {result.provider: result for result in comparison.results}
    assert results["openai"].text == "From OpenAI."
    assert results["openai"].error is None
    assert results["anthropic"].text is None
    assert results["anthropic"].error == "upstream failure"
    assert results["anthropic"].model == "claude-test"
