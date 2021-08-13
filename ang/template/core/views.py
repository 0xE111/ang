
from starlette.requests import Request
from starlette.responses import Response

from ang.templates import TemplateResponse


async def main(request: Request) -> Response:
    return TemplateResponse('core/main.html', {
        'request': request,
    })
