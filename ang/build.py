from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Iterable, List
import shutil
from ang.config import settings


def is_dev_file(file: Path) -> bool:
    return file.name[0] in {'_', '.'}


def remove(path: Path, if_: callable = lambda _: True):
    if not path.exists():
        return

    if path.is_file():
        if if_(path):
            path.unlink()
        return

    for child in path.iterdir():
        if child.is_file():
            if if_(child):
                child.unlink()
        else:
            remove(child, if_)
            if not any(child.iterdir()):
                child.rmdir()


def move_contents(source: Path, destination: Path):
    for child in source.iterdir():
        shutil.move(child, destination)
