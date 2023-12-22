import os
import shutil
import stat
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from src.domain.content import Content, ConvertionOptions


class ContentPort(ABC):
    @abstractmethod
    def get_by_url(
        self,
        project: str,
        url: str,
        **kwargs,
    ) -> Iterable[Content]:
        ...

    @abstractmethod
    def get_by_path(
        self,
        project: str,
        path: Path,
        **kwargs,
    ) -> Iterable[Content]:
        ...

    @staticmethod
    def _clear_folder(path: Path, *, mkdir: bool = True) -> None:
        def on_error(action, name, exc) -> None:
            os.chmod(name, stat.S_IWRITE)
            os.remove(name)

        if path.exists():
            shutil.rmtree(path, onerror=on_error)
        if mkdir:
            path.mkdir(parents=True, exist_ok=True)


class ContentConverterPort(ABC):
    @abstractmethod
    def convert(self, content: str, options: ConvertionOptions) -> str:
        ...
