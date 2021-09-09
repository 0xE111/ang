from ang.app import App
from starlette.routing import Route
from core import views


app = App(
    routes=[
        Route('/', views.main, name='main'),
    ],
)
