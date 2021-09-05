import logging

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from importlib import import_module

from ang.config import ROUTES_MODULE, SETTINGS_MODULE, DEBUG


settings = import_module(SETTINGS_MODULE)
logging.config.dictConfig(settings.LOGGING)
log = logging.getLogger(__name__)


if DEBUG:
    log.critical('Running application in DEBUG mode')

routes = import_module(ROUTES_MODULE)

app = Starlette(
    debug=DEBUG,
    routes=routes.ROUTES + ([
        Mount(settings.STATIC_URL, StaticFiles(directory=settings.STATIC_DIR), name='static')
    ] if DEBUG else []),
    middleware=settings.MIDDLEWARE,
)
