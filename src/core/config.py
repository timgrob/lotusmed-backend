from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Lotusmed Backend"
    APP_DESCRIPTION: str = "Backend for the Lotusmed application"
    APP_VERSION: str = "0.1.0"
    APP_DEBUG: bool = False
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    APP_RELOAD: bool = False
    APP_RELOAD_DELAY: int = 0.5
    APP_RELOAD_MAX_DELAY: int = 10.0
    APP_RELOAD_MAX_RETRIES: int = 3
    APP_API_VERSION: str = "/v1"