from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from openai import OpenAIError

from src.core.exceptions import UpstreamAIError
from src.schemas.paraphrase import ParaphraseRequest
from src.services.paraphrase import ParaphraseService

pytestmark = pytest.mark.anyio


def make_service(
    output_text: str | None = None, error: Exception | None = None
) -> tuple[ParaphraseService, AsyncMock]:
    client = AsyncMock()
    if error is not None:
        client.responses.create.side_effect = error
    else:
        client.responses.create.return_value = SimpleNamespace(output_text=output_text)
    return ParaphraseService(client=client, model="test-model"), client


async def test_paraphrase_returns_output_text():
    service, client = make_service(output_text="Plain explanation.")

    result = await service.paraphrase(ParaphraseRequest(text="Myocardial infarction."))

    assert result == "Plain explanation."
    call_kwargs = client.responses.create.call_args.kwargs
    assert call_kwargs["model"] == "test-model"
    assert call_kwargs["input"] == "Myocardial infarction."


async def test_paraphrase_defaults_to_source_language():
    service, client = make_service(output_text="Plain explanation.")

    await service.paraphrase(ParaphraseRequest(text="Myocardial infarction."))

    instructions = client.responses.create.call_args.kwargs["instructions"]
    assert (
        "Write the final text in the same language as the source text." in instructions
    )
    assert not instructions.endswith("\n")


async def test_paraphrase_includes_language_and_instructions():
    service, client = make_service(output_text="Plain explanation.")

    await service.paraphrase(
        ParaphraseRequest(
            text="Myocardial infarction.",
            target_language="German",
            instructions="Use short sentences.",
        )
    )

    instructions = client.responses.create.call_args.kwargs["instructions"]
    assert "Write the final text in German." in instructions
    assert (
        "Additional translation rules from the application owner:\nUse short sentences."
        in instructions
    )


async def test_paraphrase_openai_error():
    service, _ = make_service(error=OpenAIError("upstream failure"))

    with pytest.raises(UpstreamAIError):
        await service.paraphrase(ParaphraseRequest(text="Myocardial infarction."))


async def test_paraphrase_empty_output():
    service, _ = make_service(output_text="")

    with pytest.raises(UpstreamAIError):
        await service.paraphrase(ParaphraseRequest(text="Myocardial infarction."))
