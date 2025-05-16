from typing import TypeAlias
from uuid import uuid4

from pydantic import UUID4, BaseModel
from langchain.schema import Document as _LangchainDocument


class Content(_LangchainDocument):
    @classmethod
    def from_document(
        cls,
        document: _LangchainDocument,
        *,
        project: str,
        source: str,
        id_: UUID4 | None = None,
    ) -> "Content":
        document_dict = document.dict()
        document_dict["metadata"].update(
            {
                "project": project,
                "source": source,
                "id": id_ or uuid4().hex,
            }
        )
        return cls.parse_obj(document_dict)


ContentFormat: TypeAlias = str


class ConvertionOptions(BaseModel):
    input_format: ContentFormat
    output_format: ContentFormat

    @property
    def is_same_format(self) -> bool:
        return self.input_format == self.output_format
