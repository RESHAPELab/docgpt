from abc import ABC, abstractmethod
from typing import Iterable

from domain.content import Content, ConvertionOptions


class ContentPort(ABC):
    @abstractmethod
    def get(self, path: str) -> Iterable[Content]:
        ...


class ContentConverterPort(ABC):
    @abstractmethod
    def convert(
        self,
        content: Iterable[Content],
        options: ConvertionOptions,
    ) -> Iterable[Content]:
        ...
