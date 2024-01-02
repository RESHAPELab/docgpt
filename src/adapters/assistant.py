from functools import lru_cache

from dependency_injector.providers import Factory
from langchain.chains import ConversationalRetrievalChain
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
        k: int = 100,
        tokens_limit: int = 4_000,
        score_threshold: float | None = 0.9,
        distance_threshold: float | None = None,
    ) -> None:
        self._llm = llm

        self._storage = storage
        self._memory_factory = memory_factory
        self._k = k
        self._tokens_limit = tokens_limit
        self._score_threshold = score_threshold
        self._distance_threshold = distance_threshold

    @lru_cache
    def _get_memory(self, session_id: SessionId) -> BaseChatMemory:
        return self._memory_factory(chat_memory__session_id=session_id)

    def clear_history(self, session_id: SessionId) -> None:
        self._get_memory(session_id).clear()

    def prompt(self, message: Message, *, session_id: SessionId | None = None) -> str:
        memory = self._get_memory(session_id) if session_id else None

        qa = ConversationalRetrievalChain.from_llm(
            llm=self._llm,
            condense_question_prompt=DEFAULT_PROMPT,
            retriever=self._storage.as_retriever(
                search_type="similarity",
                search_kwargs=dict(
                    k=self._k,
                    score_threshold=self._score_threshold,
                    distance_threshold=self._distance_threshold,
                ),
            ),
            get_chat_history=lambda v: v,
            memory=memory,
            verbose=True,
            max_tokens_limit=self._tokens_limit,
        )

        qa_params = dict(question=message)
        if not memory:
            qa_params["chat_history"] = ""

        response = qa(qa_params)
        return response["answer"]
