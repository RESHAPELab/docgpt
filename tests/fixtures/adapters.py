import pytest

from src.adapters.content import WebPageContentAdapter
from src.domain.port.content import ContentPort


@pytest.fixture(params=[WebPageContentAdapter])
def content_adapter(request) -> ContentPort:
    return request.param()
