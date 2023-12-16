from abc import ABC, abstractmethod
from typing import Iterable

from src.domain.content import Content, ConvertionOptions


class ContentPort(ABC):
    @abstractmethod
    def get(
        self,
        project: str,
        *,
        url: str | None = None,
        path: str | None = None,
        clear_before: bool = False,
    ) -> Iterable[Content]:
        ...


class ContentConverterPort(ABC):
    @abstractmethod
    def convert(self, content: str, options: ConvertionOptions) -> str:
        ...
