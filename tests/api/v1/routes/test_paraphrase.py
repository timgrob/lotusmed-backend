from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx2 import AsyncClient
from openai import OpenAIError

from src.agents.openai_agent import get_agent
from src.main import app

pytestmark = pytest.mark.anyio

GENERATE_TEXT_URL = "/api/v1/paraphrase/generate-text"


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


async def test_generate_text(client: AsyncClient):
    agent = override_agent(output_text="Plain explanation.")

    response = await client.post(
        GENERATE_TEXT_URL, json={"text": "Myocardial infarction."}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"text": "Plain explanation."}
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
