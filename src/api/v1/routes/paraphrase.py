from fastapi import APIRouter

from src.api.dependencies import ParaphraseServiceDep
from src.schemas.paraphrase import ParaphraseRequest, ParaphraseResponse

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])


@router.post("/generate-text", response_model=ParaphraseResponse)
async def generate_text(
    payload: ParaphraseRequest,
    service: ParaphraseServiceDep,
) -> ParaphraseResponse:
    """Rewrite a scientific text into a more human-readable form."""
    return ParaphraseResponse(text=await service.paraphrase(payload))


# Imports needed once /generate-image is revived:
# import asyncio
# import base64
# from pathlib import Path
# from fastapi import HTTPException, status
# from openai import OpenAIError
# from src.api.dependencies import AgentDep
# from src.core.config import get_settings
# from src.prompts import load_prompt
# from src.schemas.paraphrase import MedicalImageRequest, MedicalImageResponse
# settings = get_settings()


# @router.post(
#     "/generate-image",
#     response_model=MedicalImageResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def generate_image(
#     payload: MedicalImageRequest,
#     agent: AgentDep,
# ) -> MedicalImageResponse:
#     text = payload.text.strip()
#     if not text:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Payload is required"
#         )

#     default_instructions = load_prompt("medical_depiction.md")
#     project_instructions = (
#         "Additional depiction rules from the application owner:\n"
#         f"{payload.instructions.strip()}"
#         if payload.instructions
#         else ""
#     )

#     prompt = f""""
#             Generate one medical infographic image based on the following medical text: {text} \n\n
#             When generating the image, closely follow these instructions: {default_instructions}
#             and {project_instructions}
#             """

#     try:
#         response = await agent.images.generate(
#             model=settings.OPENAI_IMAGE_MODEL_VERSION,
#             prompt=prompt,
#         )
#         image_base64 = response.data[0].b64_json
#     except OpenAIError as exc:
#         raise HTTPException(
#             status_code=status.HTTP_502_BAD_GATEWAY,
#             detail="Failed to generate medical image",
#         ) from exc

#     if not image_base64:
#         raise HTTPException(
#             status_code=status.HTTP_502_BAD_GATEWAY,
#             detail="OpenAI did not return a valid image",
#         )

#     # Save the image to a file
#     await asyncio.to_thread(
#         Path("otter.png").write_bytes, base64.b64decode(image_base64)
#     )

#     return MedicalImageResponse(image=image_base64)
