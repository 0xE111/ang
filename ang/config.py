import sys
from pathlib import Path
import logging
from importlib import import_module
from environs import Env

CORE_APP = 'core'
APP_MODULE = f'{CORE_APP}.app'
SETTINGS_MODULE = f'{CORE_APP}.settings'
BUILD_MODULE = f'{CORE_APP}.build'
ASSETS_DIR = 'assets'

ALEMBIC_INI_PATH = Path(__file__).parent / 'alembic.ini'
ALEMBIC_DIR = Path('alembic')
MIGRATIONS_DIR = ALEMBIC_DIR / 'versions'

env = Env()

ROOT = env.path('ROOT', None) or Path.cwd()
sys.path.insert(0, str(ROOT))
DEBUG = env.bool('DEBUG', False)

try:
    settings = import_module(SETTINGS_MODULE)
except ImportError:
    settings = None

if settings:
    logging.config.dictConfig(settings.LOGGING)
else:
    logging.basicConfig(level=logging.INFO)

APPS = [path for path in ROOT.iterdir() if path.is_dir() and not path.name.startswith('_')]
