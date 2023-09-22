from typing import Iterable

from domain.content import Content, ConvertionOptions
from domain.port.content import ContentConverterPort, ContentPort


class ContentService:
    _adapter: ContentPort
    _converter: ContentConverterPort

    _output_format = "markdown"

    def __init__(self, adapter: ContentPort, converter: ContentConverterPort) -> None:
        self._adapter = adapter
        self._converter = converter

    @staticmethod
    def _get_extension(path: str) -> str:
        return path.strip().rsplit(".", 1)[-1]

    def get(self, paths_set: set[str]) -> Iterable[Content]:
        for path in paths_set:
            input_format = self._get_extension(path)
            raw_content = self._adapter.get(path)

            options = ConvertionOptions(
                input_format=input_format,
                output_format=self._output_format,
            )

            content = self._converter.convert(raw_content, options)
            yield content
