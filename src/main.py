import uvicorn
from fastapi import FastAPI

from src.api.v1.routes.users import router as user_router
from src.core.config import Settings

app = FastAPI(
    title=Settings.APP_NAME,
    description=Settings.APP_DESCRIPTION,
    version=Settings.APP_VERSION
)

app.include_router(user_router, prefix=f"/api{Settings.APP_API_VERSION}")


@app.get("/")
def root():
    return {"message": "Application is running"}


if __name__ == "__main__":
    uvicorn.run(app, host=Settings.APP_HOST, port=Settings.APP_PORT)
