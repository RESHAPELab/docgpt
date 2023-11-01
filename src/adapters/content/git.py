import tempfile
from pathlib import Path
from typing import Iterable, TypeAlias

from langchain.document_loaders.git import GitLoader
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from pydantic import AnyUrl

from src.domain.content import Content
from src.domain.port.content import ContentPort

GetProps: TypeAlias = dict[Language, list[str]]


class GitCodeContentAdapter(ContentPort):
    def get(
        self,
        project: str,
        path: AnyUrl,
        props: GetProps,
        branch: str = "main",
        *,
        chunk_size: int = 2_000,
        chunk_overlap: int = 500,
    ) -> Iterable[Content]:
        url = path.unicode_string()

        for language, suffixes in props.items():

            def _file_filter(path: str) -> bool:
                path_suffixes = Path(path).suffixes
                return len(path_suffixes) > 0 and path_suffixes[0] in suffixes

            splitter = RecursiveCharacterTextSplitter.from_language(
                language,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            with tempfile.TemporaryDirectory() as tmp_dir:
                loader = GitLoader(tmp_dir, url, branch, _file_filter)
                documents = loader.load_and_split(splitter)

            for document in documents:
                yield Content.from_document(document, source=url, project=project)
