from starlette.routing import Mount
import core.routes


ROUTES = [
    Mount('/', routes=core.routes.ROUTES, name='core'),
]
