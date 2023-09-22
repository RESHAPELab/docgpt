from typing import Iterable

from domain.content import Content, ConvertionOptions
from domain.port.content import ContentConverterPort, ContentPort


class ContentService(ContentPort):
    _content_adapter: ContentPort
    _converter_adapter: ContentConverterPort

    _output_format = "markdown"

    def __init__(
        self,
        content_adapter: ContentPort,
        converter_adapter: ContentConverterPort,
    ) -> None:
        self._content_adapter = content_adapter
        self._converter_adapter = converter_adapter

    @staticmethod
    def _get_extension(path: str) -> str:
        return path.strip().rsplit(".", 1)[-1]

    def get(self, paths_set: set[str]) -> Iterable[Content]:
        for path in paths_set:
            input_format = self._get_extension(path)
            raw_content = self._content_adapter.get(path)

            options = ConvertionOptions(
                input_format=input_format,
                output_format=self._output_format,
            )

            content = self._converter_adapter.convert(raw_content, options)
            yield content
