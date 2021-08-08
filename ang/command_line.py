import shutil
from importlib import import_module
from os import environ
from pathlib import Path

import click
import uvicorn

from ang.config import root


@click.group()
def main():
    # settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    # settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    pass


def is_empty(path: Path) -> bool:
    assert path.is_dir()
    return not bool(next(path.iterdir(), None))


@main.command()
@click.argument('path', type=Path, default=Path('.'))
@click.option('--force', is_flag=True, default=False)
def init(path: Path, force: bool):
    if path.exists() and (not path.is_dir() or not is_empty(path) and not force):
        raise ValueError('Could not initialize inside non-empty folder')

    shutil.copytree(Path(__file__).parent / '_template', path, dirs_exist_ok=True)
    click.echo(f'Initialized empty project at {path}')


@main.command()
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8000)
@click.option('--reload', type=bool, default=True)
def serve(**options):
    settings = import_module('settings')
    environ['DEBUG'] = '1'

    reload_dirs = [root]
    click.echo(f'Tracking changes in {[str(dir_) for dir_ in reload_dirs]}')

    uvicorn.run(
        'ang.app:app',
        **{
            'log_level': 'debug',
            'reload_dirs': reload_dirs,
            'log_config': settings.LOGGING,
            **options,
        },
    )


if __name__ == '__main__':
    main()
