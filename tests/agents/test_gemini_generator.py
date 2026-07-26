from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from google.genai.errors import APIError

from src.agents.agentic import AIProvider
from src.agents.gemini_agent import GeminiAgent
from src.core.exceptions import UpstreamAIError

pytestmark = pytest.mark.anyio


class FakeAPIError(APIError):
    def __init__(self) -> None:
        Exception.__init__(self, "upstream failure")
        self.message = "upstream failure"
        self.code = 500
        self.status = "INTERNAL"
        self.details = None
        self.response = None


def make_generator(
    text: str | None = None, error: Exception | None = None
) -> tuple[GeminiAgent, AsyncMock]:
    client = AsyncMock()
    if error is not None:
        client.aio.models.generate_content.side_effect = error
    else:
        client.aio.models.generate_content.return_value = SimpleNamespace(text=text)
    agent = GeminiAgent(api_key="test-key")
    agent._client = client
    return agent, client


def test_provider_attribute():
    agent, _ = make_generator(text="anything")

    assert agent.provider is AIProvider.GEMINI


async def test_generate_returns_text():
    generator, client = make_generator(text="Plain explanation.")

    result = await generator.generate(
        "Some instructions.", "Myocardial infarction.", "gemini-test"
    )

    assert result == "Plain explanation."
    kwargs = client.aio.models.generate_content.call_args.kwargs
    assert kwargs["model"] == "gemini-test"
    assert kwargs["contents"] == "Myocardial infarction."
    assert kwargs["config"].system_instruction == "Some instructions."


async def test_generate_maps_sdk_error():
    generator, _ = make_generator(error=FakeAPIError())

    with pytest.raises(UpstreamAIError):
        await generator.generate(
            "Some instructions.", "Myocardial infarction.", "gemini-test"
        )


async def test_generate_empty_output():
    generator, _ = make_generator(text=None)

    with pytest.raises(UpstreamAIError):
        await generator.generate(
            "Some instructions.", "Myocardial infarction.", "gemini-test"
        )
