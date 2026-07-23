from fastapi import APIRouter

from src.api.dependencies import TranslationServiceDep
from src.core.config import get_settings
from src.schemas.paraphrase import (
    ParaphraseRequest,
    ParaphraseResponse,
    ProviderResult,
)

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])
settings = get_settings()


@router.post("/generate-text", response_model=ParaphraseResponse)
async def generate_text(
    payload: ParaphraseRequest,
    service: TranslationServiceDep,
) -> ParaphraseResponse:
    """Rewrite a scientific text into a more human-readable form."""
    return await service.paraphrase(payload)


if settings.ENVIRONMENT != "prod":

    @router.post("/compare", response_model=list[ProviderResult])
    async def compare_providers(
        payload: ParaphraseRequest,
        service: TranslationServiceDep,
    ) -> list[ProviderResult]:
        """Run the paraphrase against every configured provider (dev-only tool)."""
        return await service.paraphrase_all(payload)
