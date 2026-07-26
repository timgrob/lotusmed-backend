from fastapi import APIRouter

from src.api.dependencies import TranslationServiceDep
from src.core.config import get_settings
from src.schemas.paraphrase import (
    ParaphraseRequest,
    ParaphraseMultipleRequest,
    ProviderResult,
)

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])
settings = get_settings()


@router.post("/generate-text", response_model=ProviderResult)
async def generate_text(
    payload: ParaphraseRequest,
    service: TranslationServiceDep,
) -> ProviderResult:
    """Rewrite a scientific text into a more human-readable form."""
    return await service.paraphrase(payload)


if settings.ENVIRONMENT != "prod":

    @router.post("/generate-texts", response_model=list[ProviderResult])
    async def generate_texts(
        payload: ParaphraseMultipleRequest,
        service: TranslationServiceDep,
    ) -> list[ProviderResult]:
        """Run the paraphrase against every configured provider (dev-only tool)."""
        return await service.paraphrase_all(payload)
