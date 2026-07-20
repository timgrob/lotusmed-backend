from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.agents.base import AIProvider


class Settings(BaseSettings):
    APP_NAME: str = "Lotusmed Backend"
    APP_DESCRIPTION: str = "Backend for the Lotusmed application"
    APP_VERSION: str = "0.1.0"
    APP_DEBUG: bool = False

    APP_PORT: int = Field(default=8080, alias="APP_PORT")
    APP_HOST: str = Field(default="0.0.0.0", alias="APP_HOST")
    APP_API_VERSION: str = Field(default="v1", alias="APP_API_VERSION")

    DATABASE_URL: str = Field(alias="DATABASE_URL")

    ENVIRONMENT: str = Field(default="dev", alias="ENVIRONMENT")

    DEFAULT_AI_PROVIDER: AIProvider = "openai"
    OPENAI_API_KEY: SecretStr
    OPENAI_MODEL_VERSION: str = "gpt-5.5"
    ANTHROPIC_API_KEY: SecretStr | None = None
    ANTHROPIC_MODEL_VERSION: str = "claude-opus-4-8"
    GEMINI_API_KEY: SecretStr | None = None
    GEMINI_MODEL_VERSION: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()
