from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx2 import AsyncClient
from openai import OpenAIError

from src.agents.base import TextGenerator
from src.agents.openai_agent import get_agent
from src.api.dependencies.services import get_paraphrase_service
from src.core.exceptions import UpstreamAIError
from src.main import app
from src.services.paraphrase import ParaphraseService
from tests.fakes import FakeGenerator

pytestmark = pytest.mark.anyio

GENERATE_TEXT_URL = "/api/v1/paraphrase/generate-text"
COMPARE_URL = "/api/v1/paraphrase/compare"


def override_agent(
    output_text: str | None = None, error: Exception | None = None
) -> AsyncMock:
    agent = AsyncMock()
    if error is not None:
        agent.responses.create.side_effect = error
    else:
        agent.responses.create.return_value = SimpleNamespace(output_text=output_text)
    app.dependency_overrides[get_agent] = lambda: agent
    return agent


def override_service(
    providers: dict[str, TextGenerator], default_provider: str = "openai"
) -> ParaphraseService:
    service = ParaphraseService(providers=providers, default_provider=default_provider)
    app.dependency_overrides[get_paraphrase_service] = lambda: service
    return service


async def test_generate_text(client: AsyncClient):
    agent = override_agent(output_text="Plain explanation.")

    response = await client.post(
        GENERATE_TEXT_URL, json={"text": "Myocardial infarction."}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["text"] == "Plain explanation."
    assert data["provider"] == "openai"
    assert agent.responses.create.call_args.kwargs["input"] == "Myocardial infarction."


async def test_generate_text_forwards_language_and_instructions(client: AsyncClient):
    agent = override_agent(output_text="Plain explanation.")

    response = await client.post(
        GENERATE_TEXT_URL,
        json={
            "text": "Myocardial infarction.",
            "target_language": "German",
            "instructions": "Use short sentences.",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    instructions = agent.responses.create.call_args.kwargs["instructions"]
    assert "Write the final text in German." in instructions
    assert "Use short sentences." in instructions


async def test_generate_text_whitespace_only(client: AsyncClient):
    response = await client.post(GENERATE_TEXT_URL, json={"text": "   "})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_generate_text_openai_error(client: AsyncClient):
    override_agent(error=OpenAIError("upstream failure"))

    response = await client.post(
        GENERATE_TEXT_URL, json={"text": "Myocardial infarction."}
    )

    assert response.status_code == status.HTTP_502_BAD_GATEWAY


async def test_generate_text_empty_output(client: AsyncClient):
    override_agent(output_text="")

    response = await client.post(
        GENERATE_TEXT_URL, json={"text": "Myocardial infarction."}
    )

    assert response.status_code == status.HTTP_502_BAD_GATEWAY


async def test_generate_text_routes_to_requested_provider(client: AsyncClient):
    override_service(
        providers={
            "openai": FakeGenerator(model="gpt-test", text="From OpenAI."),
            "anthropic": FakeGenerator(model="claude-test", text="From Claude."),
        }
    )

    response = await client.post(
        GENERATE_TEXT_URL,
        json={"text": "Myocardial infarction.", "provider": "anthropic"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["text"] == "From Claude."
    assert data["provider"] == "anthropic"
    assert data["model"] == "claude-test"


async def test_generate_text_invalid_provider(client: AsyncClient):
    response = await client.post(
        GENERATE_TEXT_URL,
        json={"text": "Myocardial infarction.", "provider": "mistral"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_generate_text_unconfigured_provider(client: AsyncClient):
    override_service(providers={"openai": FakeGenerator()})

    response = await client.post(
        GENERATE_TEXT_URL,
        json={"text": "Myocardial infarction.", "provider": "anthropic"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_compare_returns_all_providers(client: AsyncClient):
    override_service(
        providers={
            "openai": FakeGenerator(model="gpt-test", text="From OpenAI."),
            "anthropic": FakeGenerator(model="claude-test", text="From Claude."),
            "gemini": FakeGenerator(
                model="gemini-test", error=UpstreamAIError("upstream failure")
            ),
        }
    )

    response = await client.post(COMPARE_URL, json={"text": "Myocardial infarction."})

    assert response.status_code == status.HTTP_200_OK
    results = {result["provider"]: result for result in response.json()["results"]}
    assert set(results) == {"openai", "anthropic", "gemini"}
    assert results["openai"]["text"] == "From OpenAI."
    assert results["anthropic"]["text"] == "From Claude."
    assert results["gemini"]["text"] is None
    assert results["gemini"]["error"] == "upstream failure"
