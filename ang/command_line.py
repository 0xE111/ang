import shutil
from importlib import import_module
from inspect import isclass
from os import chdir, environ
from pathlib import Path
from tempfile import TemporaryDirectory

import click
import uvicorn

from ang.config import APPS, ASSETS_DIR, BUILDERS_MODULE, CORE_APP, MIGRATIONS_DIR, ROOT, SETTINGS_MODULE, \
                       alembic_config
from ang.utils.paths import walk
from ang.builders import Builder

try:
    settings = import_module(SETTINGS_MODULE)
except ImportError:
    settings = None


class MisconfigurationError(Exception):
    pass


@click.group()
def main():
    # try:
    #     settings = import_module(SETTINGS_MODULE)
    # except ImportError:
    #     settings = None

    # if settings:
    #     assert isinstance(settings.STATIC_DIR, Path)
    #     settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)

    #     assert isinstance(settings.UPLOAD_DIR, Path)
    #     settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    pass


def is_empty(path: Path) -> bool:
    assert path.is_dir()
    return not bool(next(path.iterdir(), None))


@main.command()
@click.argument('path', type=Path, default=Path('.'))
@click.option('--force', is_flag=True, default=False)
def init(path: Path, force: bool):

    if path.exists() and (not path.is_dir() or not is_empty(path) and not force):
        raise FileExistsError('Could not initialize inside non-empty folder')
    shutil.copytree(Path(__file__).parent / 'template', path, dirs_exist_ok=True)

    chdir(path)
    click.echo(f'Initialized empty project at {path}')


@main.command()
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8000)
@click.option('--reload', type=bool, default=True)
def serve(**options):
    environ['DEBUG'] = '1'

    reload_dirs = [ROOT]
    click.echo(f'Tracking changes in {[str(dir_) for dir_ in reload_dirs]}')

    uvicorn.run(
        'ang.server:app',
        **{
            'log_level': 'debug',
            'reload_dirs': reload_dirs,
            'log_config': settings.LOGGING,
            **options,
        },
    )


@main.command()
def build():

    builders = import_module(BUILDERS_MODULE).BUILDERS

    with TemporaryDirectory() as build_dir:
        build_dir = Path(build_dir)
        for app in APPS:
            if not (assets_dir := app / ASSETS_DIR).exists() or not assets_dir.is_dir():
                continue

            app_build_dir = build_dir / app.name
            app_build_dir.mkdir()
            for file in walk(assets_dir):
                shutil.copy(file, app_build_dir / file.relative_to(assets_dir))

        files = (file.relative_to(build_dir) for file in walk(build_dir))
        for builder in builders:
            if not isinstance(builder, Builder):
                raise MisconfigurationError(f'Builder {builder} is not an instance of Builder class')

            click.echo(f'Running {builder}')
            files = builder(files)


if __name__ == '__main__':
    main()
