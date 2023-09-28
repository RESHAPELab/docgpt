from abc import ABC, abstractmethod

from pydantic import PositiveInt

from domain.storage import Query, QueryResult


class VectorStoragePort(ABC):
    @abstractmethod
    def search(self, query: Query, limit: PositiveInt) -> QueryResult:
        ...
