from fastapi import APIRouter, Response

from src.api.dependencies import InfographicServiceDep
from src.core.config import get_settings
from src.schemas.infographic import InfographicProviderResult, InfographicRequest

router = APIRouter(prefix="/infographic", tags=["infographic"])
settings = get_settings()


@router.post(
    "/generate",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def generate_infographic(
    payload: InfographicRequest,
    service: InfographicServiceDep,
) -> Response:
    """Render a medical report into a patient-friendly infographic image."""
    image, provider, model = await service.generate(payload)
    return Response(
        content=image,
        media_type="image/png",
        headers={"X-AI-Provider": provider, "X-AI-Model": model},
    )


if settings.ENVIRONMENT != "prod":

    @router.post("/compare", response_model=list[InfographicProviderResult])
    async def compare_providers(
        payload: InfographicRequest,
        service: InfographicServiceDep,
    ) -> list[InfographicProviderResult]:
        """Render the infographic with every configured provider (dev-only tool)."""
        return await service.generate_all(payload)
