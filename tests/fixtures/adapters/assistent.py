from typing import Any, Generator, Type

import pytest
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage

from src.adapters.assistent import OpenAiAdapater
from src.domain.port.assistent import AssistentPort


@pytest.fixture(params=[OpenAiAdapater])
def assistent_adapter(
    request,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[AssistentPort, Any, Any]:
    adapter_type: Type[AssistentPort] = request.param

    if adapter_type == OpenAiAdapater:

        def dummy_predict(*args, **kwargs):
            return AIMessage(content="fake-content")

        monkeypatch.setattr(ChatOpenAI, "predict_messages", dummy_predict)
        yield OpenAiAdapater("fake-token")
        monkeypatch.undo()
    else:
        yield adapter_type()
