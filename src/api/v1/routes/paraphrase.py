import base64
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAIError
from starlette.concurrency import run_in_threadpool

from src.agents.openai_agent import OpenAI, get_agent
from src.core.config import get_settings
from src.models.paraphrase import (
    MedicalImageRequest,
    MedicalImageResponse,
    ParaphraseRequest,
    ParaphraseResponse,
)
from src.prompts import load_prompt

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])
settings = get_settings()


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
        "Additional translation rules from the application owner:\n"
        f"{payload.instructions.strip()}"
        if payload.instructions
        else ""
    )

    try:
        response = await run_in_threadpool(
            client.responses.create,
            model=settings.OPENAI_CHATGPT_MODEL_VERSION,
            instructions=(
                f"{default_instructions}\n\n{language_instruction}\n\n{project_instructions}"
            ),
            input=text,
        )
    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate paraphrased text",
        ) from exc

    return ParaphraseResponse(text=response.output_text)


@router.post(
    "/generate-image",
    response_model=MedicalImageResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_image(
    payload: MedicalImageRequest,
    client: Annotated[OpenAI, Depends(get_agent)],
) -> MedicalImageResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payload is required")

    default_instructions = load_prompt("medical_depiction.md")
    project_instructions = (
        "Additional depiction rules from the application owner:\n"
        f"{payload.instructions.strip()}"
        if payload.instructions
        else ""
    )

    prompt = f""""
            Generate one medical infographic image based on the following medical text: {text} \n\n
            When generating the image, closely follow these instructions: {default_instructions} 
            and {project_instructions}
            """

    try:
        response = await run_in_threadpool(
            client.images.generate,
            model=settings.OPENAI_IMAGE_MODEL_VERSION,
            prompt=prompt
        )
        image_base64 = response.data[0].b64_json
    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate medical image",
        ) from exc

    if not image_base64:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI did not return a valid image",
        )

    # Save the image to a file
    with open("otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))

    return MedicalImageResponse(image=image_base64)
