import logging.config
from pathlib import Path
from re import search

from dependency_injector import containers, providers
from dependency_injector.providers import Factory, Singleton
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain_community.embeddings import HuggingFaceBgeEmbeddings, OllamaEmbeddings
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import BaseChatMessageHistory
from langchain.schema.embeddings import Embeddings
from langchain.text_splitter import TextSplitter
from langchain_community.vectorstores import VectorStore
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.pgvector import PGVector
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

from src.adapters.assistant import ConversationalAssistantAdapter
from src.adapters.content import (
    GitCodeContentAdapter,
    GitWikiContentAdapter,
    LangSplitterByMetadata,
    PandocConverterAdapter,
    WebPageContentAdapter,
)
from src.port.assistant import AssistantPort
from src.port.content import ContentConverterPort, ContentPort


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )

    assets_path = providers.Singleton(Path, ".assets")


class AI(containers.DeclarativeContainer):
    config = providers.Configuration()

    llm: Singleton[BaseChatModel] = Singleton(
        ChatOpenAI,
        model_name=config.openai.model_name,
        openai_api_key=config.openai.api_key,
        verbose=True,
    )

    openai_embedding: Singleton[Embeddings] = Singleton(
        OpenAIEmbeddings,
        model=config.openai.embedding_model_name,
        openai_api_key=config.openai.api_key,
        openai_api_version=config.openai.api_version,
        openai_api_base=config.openai.api_base,
        disallowed_special=[],
        show_progress_bar=True,
    )

    hugging_embedding: Singleton[Embeddings] = Singleton(
        HuggingFaceBgeEmbeddings,
        model_name="all-MiniLM-L6-v2",
        # model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    ollama_embedding: Singleton[Embeddings] = Singleton(
        OllamaEmbeddings,
        base_url=config.ollama.base_url,
        model="nomic-embed-text"
    )

    embeddings: Singleton[Embeddings] = ollama_embedding


class StorageAdapters(containers.DeclarativeContainer):
    config = providers.Configuration()
    ai = providers.DependenciesContainer()

    pg_vector: Singleton[VectorStore] = Singleton(
        PGVector,
        connection_string=config.vector.url,
        embedding_function=ai.embeddings,
        pre_delete_collection=config.vector.pre_delete_collection,
    )

    chroma: Singleton[VectorStore] = Singleton(
        Chroma,
        embedding_function=ai.embeddings,
        persist_directory=".localstorage",
    )

    qdrant: Singleton[VectorStore] = Singleton(
        QdrantVectorStore.from_existing_collection,
        url=config.vector.url,
        timeout=config.vector.timeout,
        collection_name=config.vector.collection_name,
        embedding=ai.embeddings,
        # retrieval_mode=RetrievalMode.HYBRID,
    )

    vector_storage: Singleton[VectorStore] = qdrant

    memory_factory: providers.Factory[BaseChatMessageHistory] = providers.Factory(
        MongoDBChatMessageHistory,
        connection_string=config.memory.url,
    )


class ContentAdapters(containers.DeclarativeContainer):
    config = providers.Configuration()
    core = providers.DependenciesContainer()

    converter: Singleton[ContentConverterPort] = Singleton(PandocConverterAdapter)
    splitter_factory: Factory[LangSplitterByMetadata] = Factory(LangSplitterByMetadata)

    git_splitter: Singleton[TextSplitter] = Singleton(splitter_factory, "file_name")
    git_code: Singleton[ContentPort] = Singleton(
        GitCodeContentAdapter,
        splitter=git_splitter,
        assets_path=core.assets_path,
    )
    git_wiki: Singleton[ContentPort] = Singleton(
        GitWikiContentAdapter,
        splitter=git_splitter,
        assets_path=core.assets_path,
    )
    web: Singleton[ContentPort] = Singleton(WebPageContentAdapter, converter)


class AssistantAdapters(containers.DeclarativeContainer):
    config = providers.Configuration()
    ai = providers.DependenciesContainer()
    storage = providers.DependenciesContainer()

    memory: providers.Factory[BaseChatMemory] = providers.Factory(
        ConversationBufferMemory,
        chat_memory=storage.memory_factory,
        memory_key="chat_history",
    )

    chat: Singleton[AssistantPort] = Singleton(
        ConversationalAssistantAdapter,
        llm=ai.llm,
        storage=storage.vector_storage,
        memory_factory=memory.provider,
        tokens_limit=config.tokens_limit.as_int(),
        search_kwargs=providers.Dict(
            k=config.k.as_int(),
            score_threshold=config.score_threshold.as_float(),
            # distance_threshold=config.distance_threshold,
        ),
    )


class Integrations(containers.DeclarativeContainer):
    config = providers.Configuration()
    assistant = providers.DependenciesContainer()

    discord_token = config.discord.token


class Api(containers.DeclarativeContainer):
    config = providers.Configuration()

    port = config.port.as_int()


class Settings(containers.DeclarativeContainer):
    config = providers.Configuration()

    core = providers.Container(Core, config=config.core)
    ai = providers.Container(AI, config=config.ai)
    storage = providers.Container(StorageAdapters, config=config.storage, ai=ai)
    content = providers.Container(ContentAdapters, config=config.content, core=core)
    assistant = providers.Container(
        AssistantAdapters,
        config=config.assistant,
        ai=ai,
        storage=storage,
    )
    app = providers.Container(Integrations, config=config.app, assistant=assistant)
    api = providers.Container(Api, config=config.api)
