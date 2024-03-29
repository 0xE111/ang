from importlib import import_module
from typing import Any

from jinja2 import Environment, FileSystemLoader, PrefixLoader, StrictUndefined, pass_context, select_autoescape
from starlette.templating import _TemplateResponse

from ang.config import SETTINGS_MODULE, APPS, DEBUG


settings = import_module(SETTINGS_MODULE)


@pass_context
def url_for(context: dict, name: str, **path_params: Any) -> str:
    request = context["request"]
    return request.url_for(name, **path_params)


env = Environment(
    loader=PrefixLoader({
        app.name: FileSystemLoader(app / 'templates')
        for app in APPS
    }),
    autoescape=select_autoescape(),
    undefined=StrictUndefined,
)
env.globals.update({
    'url_for': url_for,
    'DEBUG': DEBUG,
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
