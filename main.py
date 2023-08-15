from src.services import ScrapperService, ChatService
from pydantic_settings import BaseSettings, SettingsConfigDict
import pypandoc


class EnvSetting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    CHAT_SERVICE_TOKEN: str


if __name__ == "__main__":
    pypandoc.ensure_pandoc_installed()

    settings = EnvSetting()
    scrapperService = ScrapperService()

    context = scrapperService.get_by_url(
        "https://pandas.pydata.org/docs/dev/_sources/development/contributing.rst.txt",
        "rst",
    )

    chatService = ChatService(context, settings.CHAT_SERVICE_TOKEN)
    while True:
        question = input("> ")
        if question.lower() == "q":
            break
        response = chatService.prompt(question)
        print(response)
