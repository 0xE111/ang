import shutil
import sys
from importlib import import_module
from os import chdir, environ
from pathlib import Path
from tempfile import TemporaryDirectory

import alembic.config
import click
import uvicorn

from .config import APP_MODULE, APPS, ASSETS_DIR, BUILD_MODULE, CORE_APP, MIGRATIONS_DIR, ROOT, ALEMBIC_DIR, settings
from .utils.paths import walk
from .errors import MisconfigurationError


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
    click.echo('Building')
    build_fn = import_module(BUILD_MODULE).build

    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        # TODO: move to "collect_assets" build action
        for app in APPS:
            click.echo(f'Scanning {app}')
            if not (assets_dir := app / ASSETS_DIR).exists() or not assets_dir.is_dir():
                continue

            app_temp_dir = temp_dir / app.name
            app_temp_dir.mkdir()
            for file in walk(assets_dir):
                shutil.copy(file, app_temp_dir / file.relative_to(assets_dir))

        build_fn(temp_dir)

    click.echo('Build completed')


@main.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('alembic_args', nargs=-1, type=click.UNPROCESSED)
def db(alembic_args: list):

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
    click.echo(f'Database URL: {config.get_main_option(option)}')

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


@main.command()
def shell():
    import IPython
    # TODO: from IPython.lib.deepreload import reload
    IPython.start_ipython(argv=tuple())
    raise SystemExit


if __name__ == '__main__':
    main()
