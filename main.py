import multiprocessing
from pathlib import Path

import pypandoc
from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose
from langchain.vectorstores import VectorStore
import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import tqdm

from src.app.api import create_app, run_app
from src.app.discord import BOT
from src.core import containers
from src.domain.content import Content
from src.port.assistant import AssistantPort
from src.port.content import ContentPort

GLOBAL_SETTINGS: containers.Settings = None # type: ignore

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

class RateLimitException(Exception):
    pass

def get_storage() -> VectorStore:
    if GLOBAL_SETTINGS is None:
        load_settings()
    return GLOBAL_SETTINGS.storage.vector_storage()

@retry(
    wait=wait_exponential(multiplier=1.0, min=4, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(RateLimitException),
    reraise=True,
)
def try_add_document(doc: Content) -> str:
    storage = get_storage()
    if not storage:
        return f"Failed {doc}: VectorStore is None: Dependency injection failed or storage not initialized"
    try:
        result = storage.add_documents([doc])
        if result is None:
            return f"Success: Document {doc} processed (no return value)"
        return f"Success: Document {doc} processed"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return f"Rate limit hit for document {doc}: {e}"
        return f"Failed: HTTPError for document {doc}: {e}"
    except Exception as e:
        return f"Failed: Error for document {doc}: {e}"

@inject
def add_documents(documents: list[Content]) -> None:
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as executor:
        futures = tqdm.tqdm([executor.submit(try_add_document, doc) for doc in documents])
        results = []
        for i, future in enumerate(futures, 1):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(f"Failed: Exception in executor: {e}")
        print(f"Raw results from executor: {results}")

    fails_count = 0
    total_docs = len(documents)
    # Process results
    for i, result in enumerate(results, 1):
        if isinstance(result, str) and result.startswith("Success"):
            print(f"Document {i}/{total_docs}: {result}")
        else:
            fails_count += 1
            print(f"Document {i}/{total_docs} failed: {result}")

    if fails_count:
        print(f"{fails_count} out of {total_docs} documents failed to add")
    else:
        print(f"All {total_docs} documents processed successfully")


@inject
def fetch_documents(
    code: ContentPort = Provide[containers.Settings.content.git_code],
    wiki: ContentPort = Provide[containers.Settings.content.git_wiki],
    web: ContentPort = Provide[containers.Settings.content.web],
    assets_path: Path = Provide[containers.Settings.core.assets_path],
):
    project = "jabref"

    # code_branch = "main"
    # code_url = "https://github.com/JabRef/jabref.git"
    # code_docs = list(code.get_by_url(project, code_url, branch=code_branch))
    code_docs = code.get_by_path(project, assets_path / project)

    # wiki_url = "https://docs.jabref.org"
    # wiki_docs = list(web.get_by_url(project, wiki_url, max_deep=2))
    # from pathlib import Path
    # for i, doc in enumerate(wiki_docs):
    #     filepath = path / f"{doc.metadata['id']}.md"
    #     print(f"#{i}/{len(wiki_docs)} writing file {filepath.as_posix()}")
    #     content = f"source: {doc.metadata['source']}  \n"
    #     content += f"title: {doc.metadata['title']}  \n"
    #     content += f"description: {doc.metadata.get('description', 'None')}  \n"
    #     content += f"id: {doc.metadata['id']}  \n"
    #     content += f"\n{doc.page_content}\n"
    #     filepath.write_text(content, encoding="utf-8")

    wiki_docs = wiki.get_by_path(project, assets_path / f"{project}.wiki")

    # add_documents(list(wiki_docs))  # type: ignore
    add_documents(list(code_docs))  # type: ignore


def run_api() -> None:
    settings = load_settings()
    app = create_app(settings)
    run_app(app, settings.api.port())

def load_settings() -> containers.Settings:
    global GLOBAL_SETTINGS

    load_dotenv()
    pypandoc.ensure_pandoc_installed()

    application = containers.Settings()
    application.config.from_yaml("config.yml", envs_required=True, required=True)
    application.core.init_resources()
    application.wire(modules=[__name__, "src.app.discord"])
    set_debug(True)
    set_verbose(True)

    GLOBAL_SETTINGS = application
    return application


if __name__ == "__main__":
    load_settings()
    fetch_documents()

    # api_process = multiprocessing.Process(target=run_api)
    # discord_process = multiprocessing.Process(target=run_discord)

    # api_process.start()
    # discord_process.start()

    # api_process.join()
    # discord_process.join()

    run_terminal()
