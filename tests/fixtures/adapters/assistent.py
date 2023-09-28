from typing import Any, Generator, Type

import pytest
from langchain.llms import OpenAI

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
            return "fake-content"

        monkeypatch.setattr(OpenAI, "predict", dummy_predict)
        yield OpenAiAdapater("fake-token", [])
        monkeypatch.undo()
    else:
        yield adapter_type()
