from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.api.exception_handlers import register_exception_handlers
from src.api.v1.routes.paraphrase import router as paraphrase_router
from src.api.v1.routes.users import router as user_router
from src.core.config import get_settings
from src.db.database import create_db_and_tables

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(paraphrase_router, prefix=f"/api/{settings.APP_API_VERSION}")
app.include_router(user_router, prefix=f"/api/{settings.APP_API_VERSION}")
register_exception_handlers(app)


@app.get("/")
def root():
    return {"message": "Application is running"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
