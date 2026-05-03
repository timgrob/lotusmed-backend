import uvicorn
from fastapi import FastAPI

from src.api.v1.routes.paraphrase import router as paraphrase_router
from src.api.v1.routes.users import router as user_router
from src.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

app.include_router(user_router, prefix=f"/api{settings.APP_API_VERSION}")
app.include_router(paraphrase_router, prefix=f"/api/{settings.APP_API_VERSION}")


@app.get("/")
def root():
    return {"message": "Application is running"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
