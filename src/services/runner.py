import json
from pathlib import Path

from pydantic import validate_call

from ..dto import ProjectWrapper
from .chat import ChatService
from .scrapper import ScrapperService


class RunnerService:
    _scrapper_service: ScrapperService
    _chat_service: ChatService

    @validate_call
    def __init__(
        self,
        scrapper_service: ScrapperService,
        chat_service: ChatService,
    ) -> None:
        self._scrapper_service = scrapper_service
        self._chat_service = chat_service

    @validate_call
    def by_config_file(self, filepath: Path):
        wrapper = ProjectWrapper.from_file(filepath)

        for project in wrapper.projects:
            for config in project.config:
                content = self._scrapper_service.get_by_url(config.target)
