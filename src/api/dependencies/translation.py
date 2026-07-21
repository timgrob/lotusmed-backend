from typing import Annotated

from fastapi import Depends

from src.api.dependencies import AllAgentsDep
from src.services.translations import TranslationService


def get_translation_service(agents: AllAgentsDep) -> TranslationService:
    return TranslationService(agents=agents)


TranslationServiceDep = Annotated[TranslationService, Depends(get_translation_service)]
