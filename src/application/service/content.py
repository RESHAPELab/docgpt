from os.path import splitext
from typing import Iterable

from pydantic import FilePath, FileUrl, validate_call

from domain.content import Content, ConvertionOptions
from domain.port.content import ContentConverterPort, ContentPort


class ContentService:
    _content_adapter: ContentPort
    _converter_adapter: ContentConverterPort

    _output_format = "md"

    def __init__(
        self,
        content_adapter: ContentPort,
        converter_adapter: ContentConverterPort,
    ) -> None:
        self._content_adapter = content_adapter
        self._converter_adapter = converter_adapter

    @staticmethod
    @validate_call
    def _get_extension(path: str) -> str:
        try:
            file_path = FileUrl(path)
            _, ext = splitext(file_path.unicode_string())
            return ext[1:] or "html"
        except:
            try:
                file_path = FilePath(path)
                return file_path.suffix[1:]
            except:
                raise ValueError(f"Fail to get path '{path}' extension.")

    def get(self, paths_set: set[str]) -> Iterable[Content]:
        for path in paths_set:
            input_format = self._get_extension(path)
            raw_content = self._content_adapter.get(path)

            options = ConvertionOptions(
                input_format=input_format,
                output_format=self._output_format,
            )

            content_iter = self._converter_adapter.convert(raw_content, options)
            for content in content_iter:
                yield content
