import click
import uvicorn
from ang.app import settings, cur_dir


@click.group()
def main():
    settings.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@main.command()
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8000)
@click.option('--reload', type=bool, default=True)
def serve(**options):

    reload_dirs = [cur_dir]
    click.echo(f'Tracking changes in {[str(dir_) for dir_ in reload_dirs]}')

    uvicorn.run(
        'ang.app:app',
        **{
            'log_level': 'info',
            'reload_dirs': reload_dirs,
            **options,
        },
    )


if __name__ == '__main__':
    main()
