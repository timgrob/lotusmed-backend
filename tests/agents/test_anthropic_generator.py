from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from anthropic import APIError

from src.agents.anthropic_agent import AnthropicGenerator
from src.core.exceptions import UpstreamAIError

pytestmark = pytest.mark.anyio


class FakeAPIError(APIError):
    def __init__(self) -> None:
        Exception.__init__(self, "upstream failure")
        self.message = "upstream failure"
        self.request = None
        self.body = None


def make_generator(
    content: list | None = None,
    stop_reason: str = "end_turn",
    error: Exception | None = None,
) -> tuple[AnthropicGenerator, AsyncMock]:
    client = AsyncMock()
    if error is not None:
        client.messages.create.side_effect = error
    else:
        client.messages.create.return_value = SimpleNamespace(
            stop_reason=stop_reason, content=content or []
        )
    return AnthropicGenerator(client=client, model="claude-test"), client


async def test_generate_returns_text():
    blocks = [
        SimpleNamespace(type="thinking", text="internal"),
        SimpleNamespace(type="text", text="Plain explanation."),
    ]
    generator, client = make_generator(content=blocks)

    result = await generator.generate("Some instructions.", "Myocardial infarction.")

    assert result == "Plain explanation."
    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-test"
    assert kwargs["system"] == "Some instructions."
    assert kwargs["messages"] == [{"role": "user", "content": "Myocardial infarction."}]


async def test_generate_maps_sdk_error():
    generator, _ = make_generator(error=FakeAPIError())

    with pytest.raises(UpstreamAIError):
        await generator.generate("Some instructions.", "Myocardial infarction.")


async def test_generate_refusal():
    blocks = [SimpleNamespace(type="text", text="Partial output.")]
    generator, _ = make_generator(content=blocks, stop_reason="refusal")

    with pytest.raises(UpstreamAIError):
        await generator.generate("Some instructions.", "Myocardial infarction.")


async def test_generate_empty_output():
    generator, _ = make_generator(content=[])

    with pytest.raises(UpstreamAIError):
        await generator.generate("Some instructions.", "Myocardial infarction.")
