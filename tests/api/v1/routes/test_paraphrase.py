import pytest
from fastapi import status
from httpx2 import AsyncClient

from src.agents.agentic import AIProvider
from src.api.dependencies.agent import get_agents
from src.core.exceptions import UpstreamAIError
from src.main import app
from tests.fakes import FakeAgent

pytestmark = pytest.mark.anyio

GENERATE_URL = "/api/v1/paraphrase/generate-text"
GENERATE_MANY_URL = "/api/v1/paraphrase/generate-texts"


def override_agents(agents: dict[AIProvider, FakeAgent]) -> None:
    app.dependency_overrides[get_agents] = lambda: agents


async def test_generate_text_returns_selected_provider_and_model(client: AsyncClient):
    override_agents(
        {
            AIProvider.OPENAI: FakeAgent(provider=AIProvider.OPENAI, text="openai"),
            AIProvider.GEMINI: FakeAgent(provider=AIProvider.GEMINI, text="gemini"),
        }
    )

    response = await client.post(
        GENERATE_URL,
        json={"text": "Complex.", "provider": {"name": "gemini", "model": "gemini-x"}},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "text": "gemini",
        "provider": {"name": "gemini", "model": "gemini-x"},
        "error": None,
    }


async def test_generate_text_upstream_failure_returns_error_result(client: AsyncClient):
    override_agents(
        {
            AIProvider.OPENAI: FakeAgent(
                provider=AIProvider.OPENAI, error=UpstreamAIError("provider down")
            )
        }
    )

    response = await client.post(
        GENERATE_URL,
        json={"text": "Complex.", "provider": {"name": "openai", "model": "gpt"}},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["text"] is None
    assert "provider down" in body["error"]


async def test_generate_text_unconfigured_provider_returns_400(client: AsyncClient):
    override_agents({AIProvider.OPENAI: FakeAgent(provider=AIProvider.OPENAI)})

    response = await client.post(
        GENERATE_URL,
        json={"text": "Complex.", "provider": {"name": "anthropic", "model": "x"}},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_generate_texts_explicit_targets(client: AsyncClient):
    override_agents({AIProvider.OPENAI: FakeAgent(provider=AIProvider.OPENAI, text="ok")})

    response = await client.post(
        GENERATE_MANY_URL,
        json={
            "text": "Complex.",
            "targets": [
                {"name": "openai", "model": "gpt-5.5"},
                {"name": "openai", "model": "gpt-4o"},
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    results = response.json()
    assert [r["provider"]["model"] for r in results] == ["gpt-5.5", "gpt-4o"]
    assert all(r["text"] == "ok" for r in results)


async def test_generate_texts_reports_partial_failures(client: AsyncClient):
    override_agents(
        {
            AIProvider.OPENAI: FakeAgent(provider=AIProvider.OPENAI, text="ok"),
            AIProvider.ANTHROPIC: FakeAgent(
                provider=AIProvider.ANTHROPIC, error=UpstreamAIError("down")
            ),
        }
    )

    response = await client.post(
        GENERATE_MANY_URL,
        json={
            "text": "Complex.",
            "targets": [
                {"name": "openai", "model": "gpt"},
                {"name": "anthropic", "model": "claude"},
            ],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    results = {r["provider"]["name"]: r for r in response.json()}
    assert results["openai"]["text"] == "ok"
    assert results["openai"]["error"] is None
    assert results["anthropic"]["text"] is None
    assert "down" in results["anthropic"]["error"]
