from typing import Any, Generator, Type

import openai
import pytest

from src.adapters.assistent import OpenAiAdapater
from src.domain.port.assistent import AssistentPort


class OpenAiDummyChatCompletion(openai.ChatCompletion):
    @classmethod
    def create(cls, *args, **kwargs):
        return {"choices": [{"message": {"content": "fake-content"}}]}


@pytest.fixture(params=[OpenAiAdapater])
def assistent_adapter(
    request,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[AssistentPort, Any, Any]:
    adapter_type: Type[AssistentPort] = request.param

    if adapter_type == OpenAiAdapater:
        monkeypatch.setattr(openai, "ChatCompletion", OpenAiDummyChatCompletion)
        yield OpenAiAdapater("fake-token", [])
        monkeypatch.undo()
    else:
        yield adapter_type()
