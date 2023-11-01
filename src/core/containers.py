import logging.config
from re import M

import discord
from dependency_injector import containers, providers
from dependency_injector.providers import Singleton
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationSummaryMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores import PGVector, VectorStore

from src.adapters.assistent import ConversationalAssistentAdapter
from src.adapters.content import (
    GitCodeContentAdapter,
    PandocConverterAdapter,
    WebPageContentAdapter,
)
from src.app.discord import DiscordClient
from src.domain.port.assistent import AssistentPort
from src.domain.port.content import ContentConverterPort, ContentPort


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )


class AI(containers.DeclarativeContainer):
    config = providers.Configuration()

    llm: Singleton[BaseChatModel] = Singleton(
        ChatOpenAI,
        model_name=config.openai.model_name,
        openai_api_key=config.openai.api_key,
    )

    embeddings: Singleton[Embeddings] = Singleton(
        OpenAIEmbeddings,
        openai_api_key=config.openai.api_key,
        openai_api_version=config.openai.api_version,
        openai_api_base=config.openai.api_base,
        disallowed_special=[],
        show_progress_bar=True,
    )

    memory: Singleton[BaseChatMemory] = Singleton(
        ConversationSummaryMemory,
        llm=llm,
        memory_key="chat_history",
        return_messages=True,
    )


class StorageAdapters(containers.DeclarativeContainer):
    config = providers.Configuration()
    ai = providers.DependenciesContainer()

    vector_storage: Singleton[VectorStore] = Singleton(
        PGVector,
        connection_string=config.vector.url,
        embedding_function=ai.embeddings,
        pre_delete_collection=config.vector.pre_delete_collection,
    )


class ContentAdapters(containers.DeclarativeContainer):
    config = providers.Configuration()

    converter: Singleton[ContentConverterPort] = Singleton(PandocConverterAdapter)
    git: Singleton[ContentPort] = Singleton(GitCodeContentAdapter)
    web: Singleton[ContentPort] = Singleton(WebPageContentAdapter, converter)


class AssistentAdapters(containers.DeclarativeContainer):
    config = providers.Configuration()
    ai = providers.DependenciesContainer()
    storage = providers.DependenciesContainer()

    conversational: Singleton[AssistentPort] = Singleton(
        ConversationalAssistentAdapter,
        llm=ai.llm,
        storage=storage.vector_storage,
        memory=ai.memory,
        k=config.k,
        tokens_limit=config.tokens_limit,
        score_threshold=config.score_threshold,
        distance_threshold=config.distance_threshold,
    )


class Apps(containers.DeclarativeContainer):
    config = providers.Configuration()
    assistent = providers.DependenciesContainer()

    discord_token = config.discord.token
    discord: Singleton[DiscordClient] = Singleton(
        DiscordClient,
        intents=discord.Intents.default(),
        assistent=assistent.conversational,
    )


class Settings(containers.DeclarativeContainer):
    config = providers.Configuration()

    core = providers.Container(Core, config=config.core)
    ai = providers.Container(AI, config=config.ai)
    storage = providers.Container(StorageAdapters, config=config.storage, ai=ai)
    content = providers.Container(ContentAdapters, config=config.content)
    assistent = providers.Container(
        AssistentAdapters,
        config=config.assistent,
        ai=ai,
        storage=storage,
    )
    app = providers.Container(Apps, config=config.app, assistent=assistent)
