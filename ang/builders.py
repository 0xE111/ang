from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Iterable
import shutil


class Builder:

    def __call__(self, files: Iterable[Path]) -> Iterator[Path]:
        raise NotImplementedError(f'{self}.__call__ not implemented')

    def __str__(self) -> str:
        return str(self.__class__)


@dataclass
class SkipFiles(Builder):

    filter: callable

    def __call__(self, files: Iterable[Path]) -> Iterator[Path]:
        yield from (file for file in files if self.filter(file))


@dataclass
class SkipInternalFiles(SkipFiles):

    filter: callable = lambda file: file.name[0] not in {'_', '.'}


@dataclass
class Move(Builder):

    destination: Path
    filter: callable = lambda file: True

    def __call__(self, files: Iterable[Path]) -> Iterator[Path]:
        for file in files:
            if self.filter(file):
                shutil.move(file, self.destination)
