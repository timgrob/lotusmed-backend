from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from openai import OpenAIError

from src.agents.openai_agent import OpenAIGenerator
from src.core.exceptions import UpstreamAIError

pytestmark = pytest.mark.anyio


def make_generator(
    output_text: str | None = None, error: Exception | None = None
) -> tuple[OpenAIGenerator, AsyncMock]:
    client = AsyncMock()
    if error is not None:
        client.responses.create.side_effect = error
    else:
        client.responses.create.return_value = SimpleNamespace(output_text=output_text)
    return OpenAIGenerator(client=client, model="test-model"), client


async def test_generate_returns_text():
    generator, client = make_generator(output_text="Plain explanation.")

    result = await generator.generate("Some instructions.", "Myocardial infarction.")

    assert result == "Plain explanation."
    kwargs = client.responses.create.call_args.kwargs
    assert kwargs["model"] == "test-model"
    assert kwargs["instructions"] == "Some instructions."
    assert kwargs["input"] == "Myocardial infarction."


async def test_generate_maps_sdk_error():
    generator, _ = make_generator(error=OpenAIError("upstream failure"))

    with pytest.raises(UpstreamAIError):
        await generator.generate("Some instructions.", "Myocardial infarction.")


async def test_generate_empty_output():
    generator, _ = make_generator(output_text="")

    with pytest.raises(UpstreamAIError):
        await generator.generate("Some instructions.", "Myocardial infarction.")
