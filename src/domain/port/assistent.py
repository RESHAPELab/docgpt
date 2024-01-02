from abc import ABC, abstractmethod

from src.domain.assistent import Message


class AssistentPort(ABC):
    @abstractmethod
    def prompt(self, message: Message) -> Message:
        ...
