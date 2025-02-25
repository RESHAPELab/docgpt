import multiprocessing
from pathlib import Path
from time import sleep

import pypandoc
from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose
from langchain.vectorstores import VectorStore

from src.app.api import create_app, run_app
from src.app.discord import BOT
from src.core import containers
from src.domain.content import Content
from src.port.assistant import AssistantPort
from src.port.content import ContentPort


@inject
def run_terminal(
    chat: AssistantPort = Provide[containers.Settings.assistant.chat],
):
    while True:
        question = input("-> **Q**: ")
        if question.lower() in ["q", "quit", "exit"]:
            break

        answer = chat.prompt(question, session_id="cli")
        print(f"**-> Q: {question}\n")
        print(f"**AI**: {answer}\n")


def run_discord():
    settings = load_settings()
    BOT.run(settings.app.discord_token())


@inject
def add_documents(
    documents: list[Content],
    *,
    storage: VectorStore = Provide[containers.Settings.storage.vector_storage],
) -> None:
    fails_count = 0
    for doc in documents:
        try:
            storage.add_documents([doc])
        except (Exception,) as e:
            fails_count += 1
            print(f"Fail to add document: {e}")

    if fails_count:
        print(f"{fails_count} documents failed to add")


@inject
def fetch_documents(
    code: ContentPort = Provide[containers.Settings.content.git_code],
    # wiki: ContentPort = Provide[containers.Settings.content.git_wiki],
    web: ContentPort = Provide[containers.Settings.content.web],
    # assets_path: Path = Provide[containers.Settings.core.assets_path],
):
    project = "jabref"

    code_branch = "main"
    code_url = "https://github.com/JabRef/jabref.git"
    code_docs = code.get_by_url(project, code_url, branch=code_branch)

    wiki_url = "https://docs.jabref.org"
    wiki_docs = web.get_by_url(project, wiki_url, max_deep=2)

    add_documents(wiki_docs)  # type: ignore
    add_documents(code_docs)  # type: ignore


def run_api() -> None:
    settings = load_settings()
    app = create_app(settings)
    run_app(app, settings.api.port())

def load_settings() -> containers.Settings:
    load_dotenv()
    pypandoc.ensure_pandoc_installed()

    application = containers.Settings()
    application.config.from_yaml("config.yml", envs_required=True, required=True)
    application.core.init_resources()
    application.wire(modules=[__name__, "src.app.discord"])
    set_debug(True)
    set_verbose(True)

    return application


if __name__ == "__main__":
    load_dotenv()
    pypandoc.ensure_pandoc_installed()

    application = containers.Settings()
    application.config.from_yaml("config.yml", envs_required=True, required=True)
    application.core.init_resources()
    application.wire(modules=[__name__, "src.app.discord"])
    set_debug(True)
    set_verbose(True)

    fetch_documents()

    # api_process = multiprocessing.Process(target=run_api)
    # discord_process = multiprocessing.Process(target=run_discord)

    # api_process.start()
    # discord_process.start()

    # api_process.join()
    # discord_process.join()

    run_terminal()
