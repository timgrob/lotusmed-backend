from typing import Annotated

from fastapi import Depends

from src.api.dependencies.agent import AllAgentsDep
from src.api.dependencies.config import SettingsDep
from src.services.translations import TranslationService


def get_translation_service(
    agents: AllAgentsDep, settings: SettingsDep
) -> TranslationService:
    return TranslationService(
        agents=agents, default_models=settings.default_models()
    )


TranslationServiceDep = Annotated[TranslationService, Depends(get_translation_service)]
