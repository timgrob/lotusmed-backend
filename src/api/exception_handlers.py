from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    ProviderNotConfiguredError,
    UpstreamAIError,
)


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def already_exists_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )


async def upstream_ai_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY, content={"detail": str(exc)}
    )


async def provider_not_configured_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(AlreadyExistsError, already_exists_handler)
    app.add_exception_handler(UpstreamAIError, upstream_ai_handler)
    app.add_exception_handler(
        ProviderNotConfiguredError, provider_not_configured_handler
    )
