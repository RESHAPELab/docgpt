from pathlib import Path
from typing import Iterable

from langchain.document_loaders import RecursiveUrlLoader
from langchain.text_splitter import MarkdownTextSplitter
from pydantic import AnyUrl, validate_call
from tqdm import tqdm

from src.domain.content import Content
from src.port.content import ContentConverterPort, ContentPort, ConvertionOptions


class WebPageContentAdapter(ContentPort):
    _convertion_options = ConvertionOptions(input_format="html", output_format="md")
    _splitter = MarkdownTextSplitter()

    def __init__(self, converter: ContentConverterPort) -> None:
        self._converter = converter

    @validate_call
    def get_by_url(
        self,
        project: str,
        url: AnyUrl,
        *,
        max_deep: int | None = None,
    ) -> Iterable[Content]:
        parsed_url = url.unicode_string()
        scrapper = RecursiveUrlLoader(parsed_url, max_deep)
        docs_iter = tqdm(
            scrapper.lazy_load(),
            desc="Scrapping pages",
            unit=" pages",
        )

        for document in docs_iter:
            document.page_content = self._converter.convert(
                document.page_content,
                self._convertion_options,
            )
            splited_docs_list = self._splitter.split_documents([document])
            yield from [
                Content.from_document(doc_chunk, source=parsed_url, project=project)
                for doc_chunk in splited_docs_list
            ]

    def get_by_path(
        self,
        project: str,
        path: Path,
        **kwargs,
    ) -> Iterable[Content]:
        raise NotImplementedError()
