from importlib import import_module
from os import environ

import click
import uvicorn

from ang.config import root


@click.group()
def main():
    # settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    # settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    pass


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
