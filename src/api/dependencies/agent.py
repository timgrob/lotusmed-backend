from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI

from src.agents.openai_agent import get_agent

AgentDep = Annotated[AsyncOpenAI, Depends(get_agent)]
