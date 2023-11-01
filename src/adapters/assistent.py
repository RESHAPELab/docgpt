from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models.base import BaseChatModel
from langchain.memory.chat_memory import BaseChatMemory
from langchain.vectorstores import VectorStore

from src.domain.assistent import Message
from src.domain.port.assistent import AssistentPort


class ConversationalAssistentAdapter(AssistentPort):
    def __init__(
        self,
        llm: BaseChatModel,
        storage: VectorStore,
        memory: BaseChatMemory,
        *,
        k: int = 100,
        tokens_limit: int = 6_000,
        score_threshold: float | None = 0.9,
        distance_threshold: float | None = None,
    ) -> None:
        self._llm = llm
        self._storage = storage
        self._memory = memory
        self._k = k
        self._tokens_limit = tokens_limit
        self._score_threshold = score_threshold
        self._distance_threshold = distance_threshold

    def prompt(self, message: Message) -> str:
        qa = ConversationalRetrievalChain.from_llm(
            llm=self._llm,
            retriever=self._storage.as_retriever(
                search_type="similarity",
                search_kwargs=dict(
                    k=self._k,
                    score_threshold=self._score_threshold,
                    distance_threshold=self._distance_threshold,
                ),
            ),
            memory=self._memory,
            verbose=True,
            max_tokens_limit=self._tokens_limit,
        )

        response = qa(message)
        return response["answer"]
