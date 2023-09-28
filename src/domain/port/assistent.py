from abc import ABC, abstractmethod

from domain.assistent import Message


class AssistentPort(ABC):
    @abstractmethod
    def load_context(self, messages: list[Message]) -> None:
        ...

    @abstractmethod
    def prompt(self, message: Message) -> Message:
        ...
