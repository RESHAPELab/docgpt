from typing import TypeAlias

from langchain.llms import OpenAI
from langchain.schema import BaseMessage, SystemMessage

from domain.assistent import Message
from domain.port.assistent import AssistentPort

Token: TypeAlias = str


class OpenAiAdapater(AssistentPort):
    _llm: OpenAI
    _context: list[BaseMessage] = []

    def __init__(self, token: Token, system_messages: list[Message] = []) -> None:
        self._llm = OpenAI(openai_api_key=token)
        self._context = [SystemMessage(content=msg) for msg in system_messages]

    def prompt(self, message: Message) -> Message:
        return self._llm.predict(message)
