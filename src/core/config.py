from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
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

    OPENAI_API_KEY: SecretStr
    OPENAI_CHATGPT_MODEL_VERSION: str = "gpt-5.5"
    OPENAI_IMAGE_MODEL_VERSION: str = "gpt-image-2"
    ANTROPIC_API_KEY: SecretStr
    ANTROPIC_MODEL_VERSION: str = "opus-4.7"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()
