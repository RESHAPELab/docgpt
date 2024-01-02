import copy
from functools import cached_property, lru_cache
from typing import Annotated, Callable, List, Optional

from langchain.docstore.document import Document
from langchain.text_splitter import (
    Language,
    RecursiveCharacterTextSplitter,
    TextSplitter,
)
from pydantic import BaseModel, BeforeValidator, field_validator

__all__ = ("LangSplitterByMetadata",)

_Extension = Annotated[
    str,
    BeforeValidator(lambda v: v if v.startswith(".") else "." + v),
]


class ExtensionLanguageMap(BaseModel):
    lang_ext_map: dict[Language, set[_Extension]]

    @cached_property
    def ext_lang_map(self) -> dict[_Extension, Language]:
        data_as_map = {}
        for lang, extensions in self.lang_ext_map.items():
            for ext in extensions:
                data_as_map[ext] = lang

        return data_as_map

    @field_validator("lang_ext_map")
    @classmethod
    def _validate_data(
        cls, v: dict[Language, set[_Extension]]
    ) -> dict[Language, set[_Extension]]:
        extension_list: list[_Extension] = []
        for extensions in v.values():
            extension_list.extend(extensions)

        if len(set(extension_list)) != len(extension_list):
            raise ValueError("Extensions must be unique")
        return v


class LangSplitterByMetadata(TextSplitter):
    _lang_ext_map = ExtensionLanguageMap(
        lang_ext_map={
            Language.CPP: {"cpp", "h", "hpp", "cc", "cxx", "hxx"},
            Language.GO: {"go", "mod", "sum"},
            Language.JAVA: {"java"},
            Language.KOTLIN: {"kt", "kts", "ktm"},
            Language.JS: {"js", "jsx", "mjs", "cjs"},
            Language.TS: {"ts", "tsx", "d.ts"},
            Language.PHP: {"php"},
            Language.PROTO: {"proto"},
            Language.PYTHON: {"py"},
            Language.RST: {"rst"},
            Language.RUBY: {"rb"},
            Language.RUST: {"rs"},
            Language.SCALA: {"scala"},
            Language.SWIFT: {"swift"},
            Language.MARKDOWN: {"markdown", "mkd", "md", "mdown"},
            Language.LATEX: {"tex"},
            Language.HTML: {"htm", "html"},
            Language.SOL: {"sol"},
            Language.CSHARP: {"cs"},
            Language.COBOL: {"cob", "cbl"},
        }
    )
    _splitter_map: dict[Language, TextSplitter] = {}
    _default_splitter: RecursiveCharacterTextSplitter

    def __init__(
        self,
        filename_metadata_field: str,
        *,
        chunk_size: int = 4000,
        chunk_overlap: int = 200,
        length_function: Callable[[str], int] = len,
        keep_separator: bool = False,
        add_start_index: bool = False,
        strip_whitespace: bool = True,
    ) -> None:
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            keep_separator=keep_separator,
            add_start_index=add_start_index,
            strip_whitespace=strip_whitespace,
        )
        self._filename_metadata_field = filename_metadata_field
        self._setup()

    @lru_cache()
    def _get_splitter(self, extension: str) -> TextSplitter:
        language = self._lang_ext_map.ext_lang_map.get(extension)
        if not language:
            return self._default_splitter

        splitter = self._splitter_map.get(language, self._default_splitter)
        return splitter

    def create_documents(
        self,
        texts: List[str],
        metadatas: List[dict] | None = None,
    ) -> List[Document]:
        splitter: TextSplitter | None = None
        filename: str | None = None

        for data in metadatas or []:
            if self._filename_metadata_field in data:
                filename = str(data[self._filename_metadata_field])
                extension = filename.split(".", maxsplit=1)[-1]
                splitter = self._get_splitter(extension)
                break

        return self._create_documents(texts, metadatas, splitter=splitter)

    def _create_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        *,
        splitter: TextSplitter | None = None,
    ) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            index = -1
            for chunk in (splitter or self).split_text(text):
                metadata = copy.deepcopy(_metadatas[i])
                if self._add_start_index:
                    index = text.find(chunk, index + 1)
                    metadata["start_index"] = index
                new_doc = Document(page_content=chunk, metadata=metadata)
                documents.append(new_doc)
        return documents

    def split_text(self, text: str) -> List[str]:
        return self._default_splitter.split_text(text)

    def _setup(self) -> None:
        self._load_splitters()

    def _load_splitters(self) -> None:
        self._splitter_map = {
            lang: self._get_lang_splitter(lang) for lang in list(Language)
        }

        self._default_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            length_function=self._length_function,
            keep_separator=self._keep_separator,
            add_start_index=self._add_start_index,
            strip_whitespace=self._strip_whitespace,
        )

    def _get_lang_splitter(self, language: Language) -> TextSplitter:
        return RecursiveCharacterTextSplitter.from_language(
            language,
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            length_function=self._length_function,
            keep_separator=self._keep_separator,
            add_start_index=self._add_start_index,
            strip_whitespace=self._strip_whitespace,
        )
