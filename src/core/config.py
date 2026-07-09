from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Lotusmed Backend"
    APP_DESCRIPTION: str = "Backend for the Lotusmed application"
    APP_VERSION: str = "0.1.0"
    APP_DEBUG: bool = False

    APP_PORT: int = 8080
    APP_HOST: str = "0.0.0.0"
    APP_RELOAD: bool = False
    APP_API_VERSION: str = "v1"

    APP_ENV: str = "dev"

    DATABASE_URL: str = "sqlite+aiosqlite:///database.db"

    OPENAI_API_KEY: SecretStr
    OPENAI_MODEL_VERSION: str = "gpt-5.5"
    ANTHROPIC_API_KEY: SecretStr
    ANTHROPIC_MODEL_VERSION: str = "opus-4.7"
    GEMINI_API_KEY: SecretStr
    GEMINI_MODEL_VERSIOIN: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()
