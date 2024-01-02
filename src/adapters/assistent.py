from typing import TypeAlias

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.document_transformers import LongContextReorder
from langchain.memory import VectorStoreRetrieverMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage
from langchain.schema.vectorstore import VectorStore
from pydantic import ConfigDict, confloat, validate_call

from src.domain.assistent import Message
from src.domain.auth import Token
from src.domain.port.assistent import AssistentPort

Temperature: TypeAlias = confloat(ge=0, lt=1)  # type: ignore


class OpenAiAdapater(AssistentPort):
    _llm: ConversationChain
    _context: list[BaseMessage] = []
    _memory: VectorStoreRetrieverMemory

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        token: Token,
        vector_storage: VectorStore,
        temperature: Temperature = 0.9,
    ) -> None:
        llm_client = ChatOpenAI(openai_api_key=token, temperature=temperature)

        self._vector_storage = vector_storage
        self._retriever = self._vector_storage.as_retriever(search_kwargs=dict(k=10))
        self._memory = VectorStoreRetrieverMemory(retriever=self._retriever)

        self._llm = ConversationChain(
            llm=llm_client,
            prompt=self._default_template,
            memory=self._memory,
        )

    @property
    def _default_template(self) -> PromptTemplate:
        template = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

        Relevant pieces of previous conversation:
        {history}

        (You do not need to use these pieces of information if not relevant)

        Current conversation:
        Human: {input}
        AI:"""

        return PromptTemplate(input_variables=["history", "input"], template=template)

    def prompt(self, message: Message) -> Message:
        docs = self._retriever.get_relevant_documents(message)

        reordering = LongContextReorder()
        reordered_docs = [
            doc.page_content for doc in reordering.transform_documents(docs)
        ]

        return self._llm.run(input_documents=reordered_docs, input=message)
