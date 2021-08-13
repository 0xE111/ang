from importlib import import_module
from typing import Any

from jinja2 import Environment, FileSystemLoader, PrefixLoader, pass_context, select_autoescape, StrictUndefined
from starlette.templating import _TemplateResponse

from ang.config import get_apps

settings = import_module('settings')


@pass_context
def url_for(context: dict, name: str, **path_params: Any) -> str:
    request = context["request"]
    return request.url_for(name, **path_params)


env = Environment(
    loader=PrefixLoader({
        app.name: FileSystemLoader(app / 'templates')
        for app in get_apps()
    }),
    autoescape=select_autoescape(),
    undefined=StrictUndefined,
)
env.globals.update({
    'url_for': url_for,
    **settings.CONTEXT,
})


def TemplateResponse(
    name: str,
    context: dict,
    status_code: int = 200,
    headers: dict = None,
    media_type: str = None,
) -> _TemplateResponse:
    if "request" not in context:
        raise ValueError('context must include a "request" key')
    template = env.get_template(name)
    return _TemplateResponse(
        template,
        context,
        status_code=status_code,
        headers=headers,
        media_type=media_type,
    )
