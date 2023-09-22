import requests
from pydantic import FileUrl

from domain.content import Content
from domain.port.content import ContentPort


class WebPageContentAdapter(ContentPort):
    def get(self, path: str) -> Content:
        url = FileUrl(path)
        return requests.get(url.unicode_string()).text
