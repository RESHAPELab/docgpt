from abc import ABC, abstractmethod

from domain.content import Content


class ContentPort(ABC):
    @abstractmethod
    def get(self, path: str) -> Content:
        ...
