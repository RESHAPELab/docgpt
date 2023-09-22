from typing import Iterable

from domain.content import Content
from domain.port.content import ContentPort


class ContentService:
    _adapter: ContentPort

    def __init__(self, adapter: ContentPort) -> None:
        self._adapter = adapter

    def get(self, paths_set: set[str]) -> Iterable[Content]:
        for path in paths_set:
            yield self._adapter.get(path)
