import shutil
from os import environ, chdir
from pathlib import Path

import click
import uvicorn
import alembic
import alembic.config
from importlib import import_module
from ang.config import SETTINGS_MODULE, root


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
    shutil.copytree(Path(__file__).parent / 'template', path, dirs_exist_ok=True)

    chdir(path)
    settings = import_module(SETTINGS_MODULE)

    config = alembic.config.Config(path / '_alembic' / 'alembic.ini')
    # config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    alembic.command.init(config, path / '_alembic', template='async')

    click.echo(f'Initialized empty project at {path}')


@main.command()
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8000)
@click.option('--reload', type=bool, default=True)
def serve(**options):
    settings = import_module(SETTINGS_MODULE)
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
