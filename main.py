from pathlib import Path

import pypandoc
from dependency_injector.wiring import Provide, inject
from langchain.globals import set_debug, set_verbose
from langchain.text_splitter import Language
from langchain.vectorstores import PGVector
from pydantic import AnyUrl

from src.adapters.content.git import GitCodeContentAdapter
from src.adapters.content.web import WebPageContentAdapter
from src.app.discord import BOT
from src.core import containers
from src.domain.port.assistent import AssistentPort


@inject
def run_terminal(
    chat: AssistentPort = Provide[containers.Settings.assistant.chat],
):
    while True:
        question = input("-> **Q**: ")
        if question.lower() in ["q", "quit", "exit"]:
            break

        answer = chat.prompt(question, session_id="cli")
        print(f"**-> Q: {question}\n")
        print(f"**AI**: {answer}\n")


@inject
def run_discord(
    *,
    token: str = Provide[containers.Settings.app.discord_token],
):
    BOT.run(token)


@inject
def fetch_documents(
    git: GitCodeContentAdapter = Provide[containers.Settings.content.git],
    web: WebPageContentAdapter = Provide[containers.Settings.content.web],
    storage: PGVector = Provide[containers.Settings.storage.vector_storage],
):
    project = "firefox"
    documents = []

    git_params: dict = {}
    repo_path = Path(".assets") / "gecko-dev"
    if repo_path.exists():
        git_params["path"] = repo_path
    else:
        git_params["url"] = "ssh://git@github.com/mozilla/gecko-dev.git"

    documents.extend(git.get(project, "master", **git_params))

    documents.extend(
        web.get(
            project,
            AnyUrl("https://firefox-source-docs.mozilla.org/index.html"),
            max_deep=3,
        )
    )

    storage.add_documents(documents)


if __name__ == "__main__":
    pypandoc.ensure_pandoc_installed()

    application = containers.Settings()
    application.config.from_yaml("config.yml")
    application.core.init_resources()
    application.wire(modules=[__name__, "src.app.discord"])
    set_debug(True)
    set_verbose(True)

    fetch_documents()
    # run_terminal()
    run_discord()
