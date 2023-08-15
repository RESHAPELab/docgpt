from enum import Enum


class ChatRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
