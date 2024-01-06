from fastapi import APIRouter, Body, Depends, status

from src.app.api.deps import get_assistant
from src.domain.assistant import Message, SessionId
from src.domain.responses import AssistantPromptResponse
from src.port.assistant import AssistantPort

__all__ = ("ROUTER",)

ROUTER = APIRouter(prefix="/assistant")


@ROUTER.post("/prompt")
async def prompt(
    message: Message = Body(...),
    session_id: SessionId | None = Body(None),
    assistant: AssistantPort = Depends(get_assistant),
) -> AssistantPromptResponse:
    answer = assistant.prompt(message, session_id=session_id)

    return AssistantPromptResponse(
        question=message,
        session_id=session_id,
        answer=answer,
    )


@ROUTER.delete("/history/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(
    session_id: SessionId,
    assistant: AssistantPort = Depends(get_assistant),
) -> None:
    assistant.clear_history(session_id)
