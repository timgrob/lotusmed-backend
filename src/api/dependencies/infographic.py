from typing import Annotated

from fastapi import Depends, Request

from src.api.dependencies.agent import AllAgentsDep
from src.api.dependencies.config import SettingsDep
from src.services.html_renderer import HtmlRenderer
from src.services.infographic import InfographicService


def get_html_renderer(request: Request) -> HtmlRenderer:
    renderer: HtmlRenderer = request.app.state.html_renderer
    return renderer


HtmlRendererDep = Annotated[HtmlRenderer, Depends(get_html_renderer)]


def get_infographic_service(
    agents: AllAgentsDep, settings: SettingsDep, renderer: HtmlRendererDep
) -> InfographicService:
    return InfographicService(
        agents=agents,
        default_provider=settings.DEFAULT_AI_PROVIDER,
        renderer=renderer,
    )


InfographicServiceDep = Annotated[
    InfographicService, Depends(get_infographic_service)
]
