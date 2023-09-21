import openai
from pydantic import validate_call

from ..dto.chat import ChatCompletationProps, ChatMessage
from ..enums.chat import ChatRole


class ChatService:
    __context: list[ChatMessage]

    @validate_call
    def __init__(self, context: list[ChatMessage], token: str) -> None:
        openai.api_key = token
        self.__context = self._setup_startup_messages(context)

    def _setup_startup_messages(self, context: list[ChatMessage]) -> list[ChatMessage]:
        messages: list[ChatMessage] = [
            ChatMessage(
                role=ChatRole.system,
                content="""
                You are the greatest programmer and programming teacher of all time and you are dedicated to teaching about a project to developers of various seniorities.
                A lot of information will be given in markdown, so by default interpret it as such.
                Use only the example information, if you don't know the answer say: "I don't know about that yet". Below you have more informations about:
                """.strip(),
            )
            * context
        ]
        return messages

    def prompt(self, text: str) -> str:
        props = ChatCompletationProps(
            messages=[
                *self.__context,
                ChatMessage(role=ChatRole.user, content=text),
            ]
        )

        response = openai.ChatCompletion.create(**props.model_dump())
        response_message = response["choices"][0]["message"]
        return response_message.content
