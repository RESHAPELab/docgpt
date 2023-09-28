from typing import Iterable

import pypandoc
from langchain.document_loaders import RecursiveUrlLoader
from pydantic import FileUrl

from domain.content import Content, ConvertionOptions
from domain.port.content import ContentConverterPort, ContentPort


class WebPageContentAdapter(ContentPort):
    _max_deep: int

    def __init__(self, max_deep: int = 2) -> None:
        self._max_deep = max_deep

    def get(self, path: str) -> Iterable[Content]:
        url = FileUrl(path)
        scrapper = RecursiveUrlLoader(url.unicode_string(), max_depth=self._max_deep)
        for document in scrapper.load():
            yield document.page_content


class PandocConverterAdapter(ContentConverterPort):
    def convert(
        self,
        content_iter: Iterable[Content],
        options: ConvertionOptions | None = None,
    ) -> Iterable[Content]:
        if options is None or options.is_same_format:
            return content_iter

        for content in content_iter:
            yield pypandoc.convert_text(
                content,
                options.output_format,
                options.input_format,
            )
