from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.api.exception_handlers import register_exception_handlers
from src.api.v1.routes.infographic import router as infographic_router
from src.api.v1.routes.prompt import router as file_router
from src.api.v1.routes.paraphrase import router as paraphrase_router
from src.api.v1.routes.users import router as user_router
from src.core.config import get_settings
from src.db.database import create_db_and_tables
from src.services.html_renderer import HtmlRenderer

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    renderer = HtmlRenderer()
    await renderer.start()
    app.state.html_renderer = renderer
    try:
        yield
    finally:
        await renderer.stop()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(paraphrase_router, prefix=f"/api/{settings.APP_API_VERSION}")
app.include_router(user_router, prefix=f"/api/{settings.APP_API_VERSION}")
app.include_router(file_router, prefix=f"/api/{settings.APP_API_VERSION}")
app.include_router(infographic_router, prefix=f"/api/{settings.APP_API_VERSION}")
register_exception_handlers(app)


@app.get("/")
def root():
    return {"message": "Application is running"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
