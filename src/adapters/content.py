import pypandoc
import requests
from pydantic import FileUrl, validate_call

from domain.content import Content, ConvertionOptions
from domain.port.content import ContentConverterPort, ContentPort


class WebPageContentAdapter(ContentPort):
    def get(self, path: str) -> Content:
        url = FileUrl(path)
        return requests.get(url.unicode_string()).text


class PandocConverterAdapter(ContentConverterPort):
    @validate_call
    def convert(
        self,
        content: Content,
        options: ConvertionOptions | None = None,
    ) -> Content:
        if options is None or options.is_same_format:
            return content
        return pypandoc.convert_text(
            content,
            options.output_format,
            options.input_format,
        )
