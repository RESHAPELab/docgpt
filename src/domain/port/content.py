from abc import ABC, abstractmethod
from typing import Iterable

from src.domain.content import Content, ConvertionOptions


class ContentPort(ABC):
    @abstractmethod
    def get(self, project: str, path: str, **kwargs) -> Iterable[Content]:
        ...


class ContentConverterPort(ABC):
    @abstractmethod
    def convert(self, content: str, options: ConvertionOptions) -> str:
        ...
