from pathlib import Path
from typing import Iterable

from git import Repo
from langchain.docstore.document import Document
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import TextSplitter
from pydantic import AnyUrl, validate_call

from src.domain.content import Content
from src.port.content import ContentPort

__all__ = ("GitWikiContentAdapter",)


class GitWikiContentAdapter(ContentPort):
    def __init__(self, splitter: TextSplitter, assets_path: Path) -> None:
        self._splitter = splitter
        self._assets_path = assets_path

    def _clone_repo(self, target: Path, url: str) -> None:
        Repo.clone_from(url, target)

    def _get_docs(self, path: Path) -> Iterable[Document]:
        loader = DirectoryLoader(
            path.absolute().as_posix(),
            show_progress=True,
            use_multithreading=True,
        )

        yield from loader.load_and_split(self._splitter)

    @validate_call
    def get_by_path(self, project: str, path: Path) -> Iterable[Content]:
        for doc in self._get_docs(path):
            yield Content.from_document(
                doc,
                source=path.name,
                project=project,
            )

    @validate_call
    def get_by_url(self, project: str, url: AnyUrl) -> Iterable[Content]:
        if not url.path:
            raise ValueError("Cannot define the repository")

        url_path = url.path.rsplit("/", maxsplit=1)[-1].lower()
        if url_path.endswith("/"):
            url_path = url_path[:-1]
        if url_path.endswith(".git"):
            url_path = url_path[:-4]

        url_parts = url_path.rsplit(".", maxsplit=1)[-2:]
        if len(url_parts) != 2:
            raise ValueError("Bad format url")
        repo_name, term = url_parts

        if term.lower() != "wiki":
            raise ValueError("Url must end path as 'wiki' or 'wiki.git")

        path = self._assets_path.joinpath(f"{repo_name}.{term}")
        self._clear_folder(path, mkdir=False)
        self._clone_repo(path, url.unicode_string())

        yield from self.get_by_path(project, path)
