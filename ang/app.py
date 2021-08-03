from starlette.applications import Starlette
import sys
from importlib import import_module
from pathlib import Path


cur_dir = Path.cwd()
sys.path.insert(0, str(cur_dir))
settings = import_module('settings')

app = Starlette(
    debug=True,
    routes=settings.ROUTES,
    middleware=settings.MIDDLEWARE,
)
