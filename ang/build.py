from pathlib import Path
import shutil


def is_dev_file(file: Path) -> bool:
    return file.name[0] in {'_', '.'}


def clear(path: Path, if_: callable = lambda _: True):
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
            clear(child, if_)
            if not any(child.iterdir()):
                child.rmdir()


def move_contents(source: Path, destination: Path):
    for child in source.iterdir():
        shutil.move(child, destination)
