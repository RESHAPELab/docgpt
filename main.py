import pypandoc
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

    persona_message = """
    You are the greatest programmer and programming teacher of all time and you are dedicated to teaching about a project to developers of various seniorities.
    A lot of information will be given in markdown, so by default interpret it as such.
    Use only the example information, if you don't know the answer say: "I don't know about that yet". Below you have more informations about:
    """.strip()
    system_messages = [persona_message]

    doc_urls = set(["https://docs.qiime2.org/2023.7/about/"])

    content_adapter = WebPageContentAdapter()
    content_converter_adapter = PandocConverterAdapter()
    content_service = ContentService(content_adapter, content_converter_adapter)

    content_iter = content_service.get(doc_urls)
    system_messages.extend(content_iter)

    assistent_adapter = OpenAiAdapater(settings.CHAT_SERVICE_TOKEN, system_messages)
    assistent = AssistentService(assistent_adapter)

    while True:
        question = input("> ")
        if question.lower() == "q":
            break
        response = assistent.prompt(question)
        print(response)
