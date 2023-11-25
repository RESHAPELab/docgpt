from abc import ABC, abstractmethod

from src.domain.assistent import Message, SessionId


class AssistentPort(ABC):
    @abstractmethod
    def clear_history(self, session_id: SessionId) -> None:
        ...

    @abstractmethod
    def prompt(
        self,
        message: Message,
        *,
        session_id: SessionId | None = None,
    ) -> Message:
        ...
