from starlette.routing import Route
from core import views


ROUTES = [
    Route('/', views.main, name='main'),
]
