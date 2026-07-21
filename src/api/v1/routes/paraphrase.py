from fastapi import APIRouter
from fastapi import HTTPException

from src.api.dependencies import TranslationServiceDep
from src.core.config import get_settings
from src.schemas.paraphrase import (
    ParaphraseRequest,
    ParaphraseResponse,
)

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])
settings = get_settings()


@router.post("/generate-text", response_model=ParaphraseResponse)
async def generate_text(
    payload: ParaphraseRequest,
    service: TranslationServiceDep,
) -> ParaphraseResponse:
    """Rewrite a scientific text into a more human-readable form."""
    res = await service.paraphrase(payload)

    if res.error is not None:
        raise HTTPException(
            status_code=502,
            detail=res.error,
        )

    if res.text is None:
        raise HTTPException(
            status_code=502,
            detail="Provider returned no text",
        )

    return ParaphraseResponse(
        text=res.text,
        provider=res.provider,
        model=res.model,
    )


@router.post("/compare", response_model=list[ParaphraseResponse])
async def compare_providers(
    payload: ParaphraseRequest,
    service: TranslationServiceDep,
) -> list[ParaphraseResponse]:
    """Run the paraphrase against every configured provider (dev-only tool)."""
    results = await service.paraphrase_all(payload)
    responses = []
    for res in results:
        if res.error is not None:
            raise HTTPException(
                status_code=502,
                detail=res.error,
            )

        if res.text is None:
            raise HTTPException(
                status_code=502,
                detail="Provider returned no text",
            )

        response = ParaphraseResponse(
            text=res.text,
            provider=res.provider,
            model=res.model,
        )
        responses.append(response)

    return responses
