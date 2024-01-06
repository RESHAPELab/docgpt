from pydantic import BaseModel

__all__ = ("AssistantPromptResponse",)


class AssistantPromptResponse(BaseModel):
    question: str
    answer: str
    session_id: str | None = None
