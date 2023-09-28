from typing import TypeAlias

from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import confloat, validate_call

from domain.assistent import Message
from domain.auth import Token
from domain.port.assistent import AssistentPort

Temperature: TypeAlias = confloat(ge=0, lt=1)  # type: ignore


class OpenAiAdapater(AssistentPort):
    _llm: ChatOpenAI
    _context: list[BaseMessage] = []
    _tokenizer: RecursiveCharacterTextSplitter

    @validate_call
    def __init__(self, token: Token, temperature: Temperature = 0.9) -> None:
        self._llm = ChatOpenAI(openai_api_key=token, temperature=temperature)
        self._tokenizer = RecursiveCharacterTextSplitter().from_tiktoken_encoder(
            model_name=self._llm.model_name
        )

    def _tokens_to_msg(self, messages: list[Message]) -> list[Message]:
        doc_list = self._tokenizer.create_documents(messages)
        return [doc.page_content for doc in doc_list]

    def load_context(self, messages: list[Message]) -> None:
        self._context.clear()
        for msg in self._tokens_to_msg(messages):
            self._context.append(SystemMessage(content=msg))

    def prompt(self, message: Message) -> Message:
        human_messages = [
            HumanMessage(content=msg) for msg in self._tokens_to_msg([message])
        ]
        message_list = self._context + human_messages

        return self._llm.predict_messages(message_list).content
