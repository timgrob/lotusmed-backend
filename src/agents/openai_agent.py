from openai import OpenAI

from src.core.config import get_settings

settings = get_settings()

client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())


def get_agent() -> OpenAI:
    return client
