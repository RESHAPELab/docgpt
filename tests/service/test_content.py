from urllib.parse import urljoin

from application.service.content import ContentService


def test_content_service(
    requests_mock,
    fake,
    content_test_data,
    content_adapter,
    content_converter_adapter,
):
    service = ContentService(content_adapter, content_converter_adapter)
    input_content, output_content = content_test_data

    fake_url = urljoin(fake.url(), "/dummy.html")

    requests_mock.get(fake_url, text=input_content)

    for service_content in service.get(set([fake_url])):
        assert service_content == output_content
