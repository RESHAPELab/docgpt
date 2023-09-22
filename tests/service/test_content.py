from urllib.parse import urljoin

from faker import Faker

from application.service.content import ContentService


def test_content_service(requests_mock, fake: Faker, content_adapter):
    service = ContentService(content_adapter)

    fake_content = "<html><body>Hello world</body></html>"
    fake_url = urljoin(fake.url(), "/dummy.html")

    requests_mock.get(fake_url, text=fake_content)

    for service_content in service.get(set([fake_url])):
        assert service_content == fake_content
