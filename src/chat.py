from enum import Enum
from pydantic import BaseModel, validate_call
from .helpers import flatten_dict
import openai


class ChatRoles(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class ChatMessage(BaseModel):
    role: ChatRoles
    content: str


class ChatCompletationProps(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: list[ChatMessage]


class ChatService:
    __context: list[ChatMessage]

    @validate_call
    def __init__(self, context: dict, token: str) -> None:
        openai.api_key = token
        self.__context = self.__parse_context_messages(context)

    def __parse_context_messages(self, context: dict) -> list[ChatMessage]:
        flat_context = flatten_dict(context)

        messages: list[ChatMessage] = [
            ChatMessage(
                role=ChatRoles.system,
                content="""
                You are the greatest programmer and programming teacher of all time and you are dedicated to teaching about a project to developers of various seniorities.
                A lot of information will be given in markdown, so by default interpret it as such.
                Use only the example information, if you don't know the answer say: "I don't know about that yet". Below you have more informations about:
                """.strip(),
            )
        ]
        for key, value in flat_context.items():
            messages.extend(
                [
                    ChatMessage(
                        role=ChatRoles.system,
                        content=f"""Topic: {key}
                        Content: {value}""",
                    ),
                ]
            )
        return messages

    def prompt(self, text: str) -> str:
        props = ChatCompletationProps(
            messages=[
                *self.__context,
                ChatMessage(role=ChatRoles.user, content=text),
            ]
        )

        response = openai.ChatCompletion.create(**props.model_dump())
        response_message = response["choices"][0]["message"]
        return response_message.content
