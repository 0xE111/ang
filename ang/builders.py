from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Iterable, Union, List
import shutil
import subprocess
from ang.config import ROOT


class Builder:

    def __call__(self, files: Iterable[Path]) -> Iterator[Path]:
        raise NotImplementedError(f'{self}.__call__ not implemented')

    def __str__(self) -> str:
        return str(self.__class__)


@dataclass
class SkipFiles(Builder):

    skip_if: callable

    def __call__(self, files: Iterable[Path]) -> Iterator[Path]:
        yield from (file for file in files if not self.skip_if(file))


@dataclass
class SkipInternalFiles(SkipFiles):

    skip_if: callable = lambda file: file.name[0] in {'_', '.'}


@dataclass
class ClearDir(Builder):

    folder: Path

    @classmethod
    def clear_dir(cls, path: Path):
        for child in path.iterdir():
            if child.is_file():
                child.unlink()
            else:
                cls.clear_dir(child)
            child.rmdir()

    def __call__(self, files: Iterable[Path]) -> Iterator[Path]:
        self.clear_dir(self.folder)
        return files


@dataclass
class MoveTo(Builder):

    destination: Path
    filter: callable = lambda file: True

    def __call__(self, files: Iterable[Path]) -> Iterator[Path]:
        for file in files:
            if self.filter(file):
                destination_file_path = self.destination / file
                destination_file_path.parent.mkdir(exist_ok=True)
                shutil.move(file, destination_file_path)


@dataclass
class Run(Builder):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, files: Iterable[Path]) -> Iterator[Path]:
        subprocess.run(*self.args, **self.kwargs)
        return files
