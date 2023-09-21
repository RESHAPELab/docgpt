from collections import OrderedDict
from typing import Literal

import markdown_to_json
import pypandoc
import requests
from pydantic import AnyUrl, PositiveInt, validate_call


class ScrapperService:
    __target_format: Literal["markdown"] = "markdown"

    def __get_extension(self, filepath: str) -> str:
        return filepath.strip().rsplit(".", 1)[-1]

    def __dictify_content(
        self,
        content: str,
        content_format: str,
    ) -> OrderedDict:
        if content_format != self.__target_format:
            content = pypandoc.convert_text(
                content,
                self.__target_format,
                content_format,
            )
        return markdown_to_json.dictify(content)

    @validate_call()
    def get_by_url(
        self,
        url: AnyUrl,
        content_format: str | None = None,
        # TODO
        link_deep: PositiveInt = 0,
    ) -> OrderedDict:
        content = requests.get(url).text
        if not content_format:
            content_format = self.__get_extension(url)

        return self.__dictify_content(content, content_format)
