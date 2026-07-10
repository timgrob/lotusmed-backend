from typing import Annotated

from fastapi import Depends

from src.api.dependencies.agent import AgentDep
from src.core.config import get_settings
from src.services.paraphrase import ParaphraseService


def get_paraphrase_service(agent: AgentDep) -> ParaphraseService:
    return ParaphraseService(client=agent, model=get_settings().OPENAI_MODEL_VERSION)


ParaphraseServiceDep = Annotated[ParaphraseService, Depends(get_paraphrase_service)]
