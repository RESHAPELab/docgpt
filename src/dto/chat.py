from pydantic import BaseModel, Field, field_validator

from ..enums.chat import ChatRole


class ChatMessage(BaseModel):
    role: ChatRole
    content: str = Field(min_length=50)
    tags: list[str] | None = None

    @property
    def prompt(self) -> str:
        return f"Tags: {', '.join(self.tags)}\nContent: {self.content}"


# TODO: Exclude tags e use prompt to compose content
class ChatCompletationProps(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: list[ChatMessage]
