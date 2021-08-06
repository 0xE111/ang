from starlette.templating import Jinja2Templates

from ang.config import root


templates = Jinja2Templates(directory=root / 'templates')
TemplateResponse = templates.TemplateResponse
