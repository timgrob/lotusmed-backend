from openai import AsyncOpenAI

from src.core.config import get_settings

settings = get_settings()

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    timeout=60.0,
    max_retries=2,
)


def get_agent() -> AsyncOpenAI:
    return client
