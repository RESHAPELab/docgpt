from typing import Any, Generator, Type

import faiss
import pytest
from langchain.chains import ConversationChain
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import FakeEmbeddings
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores import FAISS

from src.adapters.assistent import OpenAiAdapater
from src.domain.port.assistent import AssistentPort


@pytest.fixture
def assistent_token():
    return "fake-token"


@pytest.fixture
def embedding_size():
    return 1536


@pytest.fixture
def embeddings(embedding_size) -> Embeddings:
    return FakeEmbeddings(size=embedding_size)


@pytest.fixture
def vector_storage(fake, embeddings: Embeddings, embedding_size):
    index = faiss.IndexFlatL2(embedding_size)
    storage = FAISS(embeddings.embed_query, index, InMemoryDocstore({}), {})

    storage.add_texts([fake.text() for i in range(10)])

    return storage


@pytest.fixture(params=[OpenAiAdapater])
def assistent_adapter(
    request,
    assistent_token,
    vector_storage,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[AssistentPort, Any, Any]:
    adapter_type: Type[AssistentPort] = request.param

    if adapter_type == OpenAiAdapater:

        def dummy_predict(*args, **kwargs):
            return "fake-content"

        monkeypatch.setattr(ConversationChain, "predict", dummy_predict)
        yield OpenAiAdapater(assistent_token, vector_storage)
        monkeypatch.undo()
    else:
        yield adapter_type()
