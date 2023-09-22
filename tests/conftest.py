import pytest
from faker import Faker

from .fixtures import *


@pytest.fixture(scope="session")
def fake() -> Faker:
    return Faker()
