from typing import Iterable

from langchain.document_loaders import RecursiveUrlLoader
from pydantic import AnyUrl
from sqlalchemy import desc
from tqdm import tqdm

from src.domain.content import Content
from src.domain.port.content import ContentConverterPort, ContentPort, ConvertionOptions


class WebPageContentAdapter(ContentPort):
    _convertion_options = ConvertionOptions(input_format="html", output_format="md")

    def __init__(self, converter: ContentConverterPort) -> None:
        self._converter = converter

    def get(
        self,
        project: str,
        path: AnyUrl,
        *,
        max_deep: int = 2,
    ) -> Iterable[Content]:
        url = path.unicode_string()
        scrapper = RecursiveUrlLoader(url, max_deep)
        docs_iter = tqdm(
            scrapper.load_and_split(),
            desc="Scrapping pages",
            unit=" pages",
        )

        for document in docs_iter:
            document.page_content = self._converter.convert(
                document.page_content,
                self._convertion_options,
            )
            yield Content.from_document(document, source=url, project=project)
