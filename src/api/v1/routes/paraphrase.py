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
