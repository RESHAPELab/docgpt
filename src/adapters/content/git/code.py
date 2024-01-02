import multiprocessing as mp
import os
from pathlib import Path
from typing import AnyStr, Callable, Iterable, Iterator, TypeAlias

from git import Repo
from git.objects import Blob, Submodule, Tree
from langchain.docstore.document import Document
from langchain.document_loaders.git import GitLoader as BaseGitLoader
from langchain.text_splitter import TextSplitter
from pydantic import AnyUrl, validate_call
from tqdm import tqdm

from src.domain.content import Content
from src.port.content import ContentPort

__all__ = ("GitCodeContentAdapter",)

_IndexObjUnion: TypeAlias = Tree | Blob | Submodule
_TraversedTreeTup: TypeAlias = (
    tuple[Tree | None] | _IndexObjUnion | tuple[Submodule, Submodule]
)
_Item: TypeAlias = _IndexObjUnion | _TraversedTreeTup


class _GitLoader(BaseGitLoader):
    @staticmethod
    def _process_item(
        data: tuple[
            _Item,
            str,
            Callable[[str], bool] | None,
            Callable[..., list[str]],
        ],
    ) -> Document | None:
        item, repo_path, file_filter, check_ignore = data
        if not isinstance(item, Blob):
            return None

        file_path = os.path.join(repo_path, item.path)

        ignored_files = check_ignore(
            [file_path]
        )  # repo.ignored([file_path])  # type: ignore
        if len(ignored_files):
            return None

        # uses filter to skip files
        if file_filter and not file_filter(file_path):
            return None

        rel_file_path = os.path.relpath(file_path, repo_path)
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                # file_type = os.path.splitext(item.name)[1]

                # loads only text files
                try:
                    text_content = content.decode("utf-8")
                except UnicodeDecodeError:
                    return None

                metadata = {
                    "source": rel_file_path,
                    "file_path": rel_file_path,
                    "file_name": item.name,
                    # "file_type": file_type,
                }
                doc = Document(page_content=text_content, metadata=metadata)
                return doc
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def _iter_tree(
        self, repo: Repo
    ) -> Iterator[
        tuple[
            _Item,
            str,
            Callable[[str], bool] | None,
            Callable[..., list[str]],
        ]
    ]:
        for item in repo.tree().traverse():
            yield item, self.repo_path, self.file_filter, repo.ignored  # type: ignore

    def load(self) -> list[Document]:
        try:
            from git import Blob, Repo  # type: ignore
        except ImportError as ex:
            raise ImportError(
                "Could not import git python package. "
                "Please install it with `pip install GitPython`."
            ) from ex

        if not os.path.exists(self.repo_path) and self.clone_url is None:
            raise ValueError(f"Path {self.repo_path} does not exist")
        elif self.clone_url:
            # If the repo_path already contains a git repository, verify that it's the
            # same repository as the one we're trying to clone.
            if os.path.isdir(os.path.join(self.repo_path, ".git")):
                repo = Repo(self.repo_path)
                # If the existing repository is not the same as the one we're trying to
                # clone, raise an error.
                if repo.remotes.origin.url != self.clone_url:
                    raise ValueError(
                        "A different repository is already cloned at this path."
                    )
            else:
                repo = Repo.clone_from(self.clone_url, self.repo_path)
            repo.git.checkout(self.branch)
        else:
            repo = Repo(self.repo_path)
            repo.git.checkout(self.branch)

        iter_tree = tqdm(self._iter_tree(repo), desc="Processing files", unit=" files")

        with mp.Pool(processes=mp.cpu_count()) as pool:
            result_iter = pool.imap_unordered(
                self._process_item,
                iter_tree,  # type:ignore
            )

            return [doc for doc in result_iter if doc is not None]


class GitCodeContentAdapter(ContentPort):
    def __init__(self, splitter: TextSplitter, assets_path: Path) -> None:
        self._splitter = splitter
        self._assets_path = assets_path

    def _get_documents(
        self,
        project: str,
        *,
        repo_path: Path,
        clone_url: AnyUrl | None = None,
        branch: str | None = "main",
        file_filter: Callable[[str], bool] | None = None,
    ) -> Iterable[Content]:
        loader = _GitLoader(
            repo_path.absolute().as_posix(),
            clone_url.unicode_string() if clone_url else None,
            branch,
            file_filter,
        )

        documents = loader.load_and_split(self._splitter)

        for document in documents:
            yield Content.from_document(
                document,
                source=repo_path.name,
                project=project,
            )

    @validate_call
    def get_by_path(
        self,
        project: str,
        path: Path,
        *,
        branch: str = "main",
    ) -> Iterable[Content]:
        yield from self._get_documents(
            project,
            repo_path=path,
            branch=branch,
        )

    @validate_call
    def get_by_url(
        self,
        project: str,
        url: AnyUrl,
        *,
        branch: str = "main",
    ) -> Iterator[Content]:
        if not url.path:
            raise ValueError("Cannot define the repository")

        repo_name = url.path.rsplit("/", maxsplit=1)[-1].lower()
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        path = self._assets_path.joinpath(repo_name)
        self._clear_folder(path, mkdir=False)

        yield from self._get_documents(
            project,
            repo_path=path,
            clone_url=url,
            branch=branch,
        )
