from abc import ABC, abstractmethod

from domain.content import Content, ConvertionOptions


class ContentPort(ABC):
    @abstractmethod
    def get(self, path: str) -> Content:
        ...


class ContentConverterPort(ABC):
    @abstractmethod
    def convert(self, content: Content, options: ConvertionOptions) -> Content:
        ...
