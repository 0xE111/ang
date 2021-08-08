import logging

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from importlib import import_module

from ang.config import env, settings


logging.config.dictConfig(settings.LOGGING)
log = logging.getLogger(__name__)


if debug := env.bool('DEBUG', False):
    log.critical('Running application in DEBUG mode')

routes = import_module('routes')

app = Starlette(
    debug=debug,
    routes=routes.ROUTES + ([
        Mount('/static', StaticFiles(directory=settings.STATIC_DIR), name='static')
    ] if debug else []),
    middleware=settings.MIDDLEWARE,
)
