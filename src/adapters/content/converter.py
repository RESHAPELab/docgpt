import pypandoc

from src.domain.content import ConvertionOptions
from src.port.content import ContentConverterPort


class PandocConverterAdapter(ContentConverterPort):
    def convert(
        self,
        content: str,
        options: ConvertionOptions | None = None,
    ) -> str:
        if options is None or options.is_same_format:
            return content

        return pypandoc.convert_text(
            content,
            options.output_format,
            options.input_format,
        )
