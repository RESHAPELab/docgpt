from pydantic import BaseModel

from ..enums.chat import ChatRole


class ChatMessage(BaseModel):
    role: ChatRole
    content: str


class ChatCompletationProps(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: list[ChatMessage]
