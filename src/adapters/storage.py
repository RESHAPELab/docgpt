from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from pydantic import PositiveInt, validate_call

from domain.auth import Token
from domain.port.storage import VectorStoragePort
from domain.storage import Query, QueryResult


class ChromaOpenAiAdapter(VectorStoragePort):
    _openai_token: str
    _embedding: OpenAIEmbeddings
    _db: Chroma

    def __init__(self, documents: list[Document], token: Token) -> None:
        self._embedding = OpenAIEmbeddings(openai_api_key=token)
        self._db = Chroma.from_documents(documents, self._embedding)

    @validate_call
    def search(self, query: Query, limit: PositiveInt) -> QueryResult:
        return [doc.page_content for doc in self._db.similarity_search(query, limit)]
