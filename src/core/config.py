from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Lotusmed Backend"
    APP_DESCRIPTION: str = "Backend for the Lotusmed application"
    APP_VERSION: str = "0.1.0"
    APP_DEBUG: bool = False
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    APP_RELOAD: bool = False
    APP_API_VERSION: str = "/v1"

    model_config = SettingsConfigDict(
        env_file="../../.env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()

