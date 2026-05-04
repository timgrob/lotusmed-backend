from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAIError
from starlette.concurrency import run_in_threadpool

from src.agents.openai_agent import OpenAI, get_agent
from src.models.paraphrase import ParaphraseRequest, ParaphraseResponse
from src.prompts import load_prompt

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])


@router.post(
    "/generate-text",
    response_model=ParaphraseResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_text(
    payload: ParaphraseRequest,
    client: Annotated[OpenAI, Depends(get_agent)],
) -> ParaphraseResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payload is required")

    default_instructions = load_prompt("medical_translation.md")
    language_instruction = (
        f"Write the final text in {payload.target_language}."
        if payload.target_language
        else "Write the final text in the same language as the source text."
    )
    project_instructions = (
        "\n\nAdditional translation rules from the application owner:\n"
        f"{payload.instructions.strip()}"
        if payload.instructions
        else ""
    )

    try:
        response = await run_in_threadpool(
            client.responses.create,
            model="gpt-5.5",
            instructions=(
                f"{default_instructions}\n\n{language_instruction}{project_instructions}"
            ),
            input=text,
        )
    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate paraphrased text",
        ) from exc

    return ParaphraseResponse(text=response.output_text)


@router.post("/generate-image")
async def generate_image(payload: str, client: Annotated[OpenAI, Depends(get_agent)]):
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payload is required")
    return payload
