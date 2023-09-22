from abc import ABC, abstractmethod

from domain.assistent import Message


class AssistentPort(ABC):
    @abstractmethod
    def prompt(self, message: Message) -> Message:
        ...
