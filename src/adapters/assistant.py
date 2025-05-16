from functools import lru_cache
from typing import Any

from dependency_injector.providers import Factory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chat_models.base import BaseChatModel
from langchain.memory.chat_memory import BaseChatMemory
from langchain.vectorstores import VectorStore

from src.core.prompts import DEFAULT_PROMPT
from src.domain.assistant import Message, SessionId
from src.port.assistant import AssistantPort


class ConversationalAssistantAdapter(AssistantPort):
    def __init__(
        self,
        llm: BaseChatModel,
        storage: VectorStore,
        memory_factory: Factory[BaseChatMemory],
        *,
        search_kwargs: dict[str, Any] | None = None,
        tokens_limit: int = 4_000,
    ) -> None:
        self._llm = llm

        self._storage = storage
        self._memory_factory = memory_factory
        self._tokens_limit = tokens_limit
        self._search_kwargs = search_kwargs
        for k, v in self._search_kwargs.items():
            if v is None:
                del self._search_kwargs[k]

    @lru_cache
    def _get_memory(self, session_id: SessionId) -> BaseChatMemory:
        return self._memory_factory(chat_memory__session_id=session_id)

    def clear_history(self, session_id: SessionId) -> None:
        self._get_memory(session_id).clear()

    def prompt(self, message: Message, *, session_id: SessionId | None = None) -> str:
        memory = self._get_memory(session_id) if session_id else None

        retriever = self._storage.as_retriever(
            search_type="similarity", search_kwargs=self._search_kwargs or None
        )

        qa = ConversationalRetrievalChain.from_llm(
            llm=self._llm,
            condense_question_prompt=DEFAULT_PROMPT,
            retriever=retriever,
            get_chat_history=lambda v: v,
            memory=memory,
            verbose=True,
            max_tokens_limit=self._tokens_limit,
        )

        qa_params = dict(question=message)
        if not memory:
            qa_params["chat_history"] = ""

        # docs: list[Document] = retriever.get_relevant_documents(message)
        # qa_params["context"] = "\n\n".join(doc.page_content for doc in docs)

        response = qa(qa_params)
        return response["answer"]
