from enum import Enum
from typing import TypeAlias

import openai
from pydantic import BaseModel, Field

from domain.assistent import Message
from domain.port.assistent import AssistentPort

Token: TypeAlias = str


class _ChatRoles(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class _ChatMessage(BaseModel):
    role: _ChatRoles
    content: Message


class _ChatCompletationProps(BaseModel):
    model: str = Field(default="gpt-3.5-turbo", frozen=True)
    messages: list[_ChatMessage] = []


class _ChatResponseMessageContent(BaseModel):
    content: str


class _ChatResponseMessage(BaseModel):
    message: _ChatResponseMessageContent


class _ChatResponse(BaseModel):
    choices: list[_ChatResponseMessage]

    @property
    def best_answer(self) -> str:
        if not self.choices:
            raise ValueError("Choices was not provided by assistent")
        return self.choices[0].message.content


class OpenAiAdapater(AssistentPort):
    _context: list[_ChatMessage] = []

    def __init__(self, token: Token, system_messages: list[Message] = []) -> None:
        openai.api_key = token

        props = _ChatCompletationProps()
        for message in system_messages:
            props.messages.append(
                _ChatMessage(
                    role=_ChatRoles.system,
                    content=message,
                )
            )

    def prompt(self, message: Message) -> Message:
        props = _ChatCompletationProps(
            messages=[
                *self._context,
                _ChatMessage(role=_ChatRoles.user, content=message),
            ]
        )

        raw_response = openai.ChatCompletion.create(**props.model_dump())
        response = _ChatResponse.model_validate(raw_response)

        return response.best_answer
