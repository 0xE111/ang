
from logging import getLogger

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from ang.config import DEBUG, settings

log = getLogger(__name__)


class App(Starlette):

    def __init__(self, *args, **kwargs):
        if DEBUG:
            log.critical('Debug mode ON')
        kwargs.setdefault('debug', DEBUG)
        kwargs.setdefault('routes', []).extend([
            Mount(settings.STATIC_URL, StaticFiles(directory=settings.BUILD_DIR), name='static'),
            Mount(settings.UPLOADS_URL, StaticFiles(directory=settings.UPLOADS_DIR), name='uploads'),
        ])
        super().__init__(*args, **kwargs)
