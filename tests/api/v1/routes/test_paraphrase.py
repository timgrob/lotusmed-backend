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
COMPARE_URL = "/api/v1/paraphrase/compare"


def override_agents(agents: dict[AIProvider, FakeAgent]) -> None:
    app.dependency_overrides[get_agents] = lambda: agents


async def test_generate_text_returns_selected_provider(client: AsyncClient):
    override_agents(
        {
            AIProvider.OPENAI: FakeAgent(provider=AIProvider.OPENAI, text="openai"),
            AIProvider.GEMINI: FakeAgent(
                provider=AIProvider.GEMINI, model="gemini-x", text="gemini"
            ),
        }
    )

    response = await client.post(
        GENERATE_URL, json={"text": "Complex.", "provider": "gemini"}
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body == {"text": "gemini", "provider": "gemini", "model": "gemini-x"}


async def test_generate_text_upstream_failure_returns_502(client: AsyncClient):
    override_agents(
        {
            AIProvider.OPENAI: FakeAgent(
                provider=AIProvider.OPENAI, error=UpstreamAIError("provider down")
            )
        }
    )

    response = await client.post(GENERATE_URL, json={"text": "Complex."})

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert response.json()["detail"] == "provider down"


async def test_generate_text_unconfigured_provider_returns_400(client: AsyncClient):
    override_agents({AIProvider.OPENAI: FakeAgent(provider=AIProvider.OPENAI)})

    response = await client.post(
        GENERATE_URL, json={"text": "Complex.", "provider": "anthropic"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_compare_returns_partial_results(client: AsyncClient):
    override_agents(
        {
            AIProvider.OPENAI: FakeAgent(provider=AIProvider.OPENAI, text="ok"),
            AIProvider.ANTHROPIC: FakeAgent(
                provider=AIProvider.ANTHROPIC, error=UpstreamAIError("down")
            ),
        }
    )

    response = await client.post(COMPARE_URL, json={"text": "Complex."})

    assert response.status_code == status.HTTP_200_OK
    results = {r["provider"]: r for r in response.json()}
    assert results["openai"]["text"] == "ok"
    assert results["openai"]["error"] is None
    assert results["anthropic"]["text"] is None
    assert results["anthropic"]["error"] == "down"
