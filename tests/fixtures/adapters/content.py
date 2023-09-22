import pytest

from src.adapters.content import PandocConverterAdapter, WebPageContentAdapter
from src.domain.port.content import ContentConverterPort, ContentPort


@pytest.fixture(params=[WebPageContentAdapter])
def content_adapter(request) -> ContentPort:
    return request.param()


@pytest.fixture(params=[PandocConverterAdapter])
def content_converter_adapter(request) -> ContentConverterPort:
    return request.param()


@pytest.fixture
def content_test_data(content_adapter) -> tuple[str, str]:
    adapter_type = type(content_adapter)

    if adapter_type == WebPageContentAdapter:
        input_content = """
        <html>
            <body>
                <h1>Topic</h1>
                <p>Hello world</p>
            </body>
        </html>
        """
        output_content = "# Topic\r\n\r\nHello world\r\n"

        return input_content, output_content
    else:
        raise NotImplementedError(
            f"Content not implement for adapter {adapter_type.__name__}"
        )
