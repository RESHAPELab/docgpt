from collections import OrderedDict
import markdown_to_json
from pydantic import AnyUrl
import requests
import pypandoc

MARKDOWN_FORMAT = "markdown"


class ScrapperService:
    def get_by_url(self, url: AnyUrl, content_format=MARKDOWN_FORMAT) -> OrderedDict:
        content = requests.get(url).text
        return self.__dictify_content(content, content_format)

    def __dictify_content(self, content: str, content_format: str) -> OrderedDict:
        if content_format not in pypandoc.get_pandoc_formats()[1]:
            raise Exception(f"{content_format} is not supported by pandoc")

        if content_format != MARKDOWN_FORMAT:
            content = pypandoc.convert_text(content, MARKDOWN_FORMAT, content_format)
        return markdown_to_json.dictify(content)
