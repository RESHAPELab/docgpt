import faiss
import pypandoc
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.adapters.assistent import OpenAiAdapater
from src.adapters.content import PandocConverterAdapter, WebPageContentAdapter
from src.application.service.assistent import AssistentService
from src.application.service.content import ContentService


class EnvSetting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    CHAT_SERVICE_TOKEN: str


if __name__ == "__main__":
    pypandoc.ensure_pandoc_installed()

    settings = EnvSetting()  # type: ignore

    doc_urls = set(["https://docs.qiime2.org/2023.7/"])

    content_adapter = WebPageContentAdapter(max_deep=2)
    content_converter_adapter = PandocConverterAdapter()
    content_service = ContentService(content_adapter, content_converter_adapter)

    content_iter = list(content_service.get(doc_urls))

    embedding_size = 1536  # Dimensions of the OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(openai_api_key=settings.CHAT_SERVICE_TOKEN)
    vector_index = faiss.IndexFlatL2(embedding_size)
    vector_storage = FAISS(
        embeddings.embed_query, vector_index, InMemoryDocstore({}), {}
    )
    vector_storage.add_texts(content_iter)

    assistent_adapter = OpenAiAdapater(settings.CHAT_SERVICE_TOKEN, vector_storage)
    assistent = AssistentService(assistent_adapter)

    while True:
        question = input("> ")
        if question.lower() == "q":
            break
        response = assistent.prompt(question)
        print(response)
