from fastapi import APIRouter

from src.api.dependencies import ParaphraseServiceDep
from src.core.config import get_settings
from src.schemas.paraphrase import (
    ParaphraseComparisonResponse,
    ParaphraseRequest,
    ParaphraseResponse,
)

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])
settings = get_settings()


@router.post("/generate-text", response_model=ParaphraseResponse)
async def generate_text(
    payload: ParaphraseRequest,
    service: ParaphraseServiceDep,
) -> ParaphraseResponse:
    """Rewrite a scientific text into a more human-readable form."""
    return await service.paraphrase(payload)


if settings.ENVIRONMENT != "prod":

    @router.post("/compare", response_model=ParaphraseComparisonResponse)
    async def compare_providers(
        payload: ParaphraseRequest,
        service: ParaphraseServiceDep,
    ) -> ParaphraseComparisonResponse:
        """Run the paraphrase against every configured provider (dev-only tool)."""
        return await service.paraphrase_all(payload)
