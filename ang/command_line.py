import shutil
import sys
from importlib import import_module
from os import chdir, environ
from pathlib import Path
from tempfile import TemporaryDirectory

import alembic.config
import click
import uvicorn

from .builders import Builder
from .config import APP_MODULE, APPS, ASSETS_DIR, BUILDERS_MODULE, CORE_APP, MIGRATIONS_DIR, ROOT, SETTINGS_MODULE, ALEMBIC_DIR, settings
from .utils.paths import walk


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
        f'{APP_MODULE}:app',
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
            files = builder(files, build_dir)


@main.command(context_settings=dict(ignore_unknown_options=True))
# @click.argument('app', type=str)
@click.argument('alembic_args', nargs=-1, type=click.UNPROCESSED)
def db(alembic_args: list):

    # if app not in {app.name for app in APPS}:
    #     raise MisconfigurationError(f'Unknown app "{app}", available apps: {APPS}')

    if not alembic_args:
        raise MisconfigurationError('Missing alembic args')

    if not settings:
        raise MisconfigurationError('Unable to load settings')

    lib_dir = Path(__file__).resolve().parent
    alembic_cli = alembic.config.CommandLine()
    options = alembic_cli.parser.parse_args(alembic_args)

    # use per-project alembic.ini file if it exists,
    # otherwise fallback to default one
    ini_path = Path(options.config)
    if not ini_path.is_absolute():
        ini_path = ROOT / ini_path
    if not ini_path.exists():
        ini_path = lib_dir / 'alembic.ini'
    click.echo(f'Alembic.ini location: {ini_path}')

    config = alembic.config.Config(
        file_=ini_path,
        ini_section=options.name,
        cmd_opts=options,
    )

    # use config-defined database url if exists,
    # otherwise fallback to settings.DATABASE_URL
    option = 'sqlalchemy.url'
    if not config.get_main_option(option):
        config.set_main_option(option, settings.DATABASE_URL)
    click.echo(f'Database DSN: {config.get_main_option(option)}')

    # use per-app alembic folder if it exists,
    # otherwise fallback to default one
    if (script_location := config.get_main_option('script_location')):
        click.echo(f'Ignoring {script_location=}')

    script_location = Path(ROOT / CORE_APP / ALEMBIC_DIR)
    if not (script_location / 'env.py').exists():
        script_location = lib_dir / ALEMBIC_DIR
    config.set_main_option('script_location', str(script_location.resolve()))
    click.echo(f'Script location: {script_location}')

    versions_location = ROOT / CORE_APP / MIGRATIONS_DIR
    click.echo(f'Version locations: {versions_location}')
    versions_location.mkdir(parents=True, exist_ok=True)
    config.set_main_option('version_locations', str(versions_location.resolve()))

    for app in APPS:
        import_module(f'{app.name}.models')

    exit(alembic_cli.run_cmd(config, options))


if __name__ == '__main__':
    main()
