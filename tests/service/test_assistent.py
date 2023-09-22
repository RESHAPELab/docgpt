from src.application.service.assistent import AssistentService
from src.domain.assistent import Message


def test_assistent_service(fake, assistent_adapter):
    service = AssistentService(assistent_adapter)
    response = service.prompt(fake.pystr())

    assert type(response) == Message
