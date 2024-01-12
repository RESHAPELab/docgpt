from fastapi import Request

from src.port.assistant import AssistantPort


def get_assistant(request: Request) -> AssistantPort:
    return request.app.container.assistant.chat()
