import sys
from pathlib import Path

from alembic.config import Config
from environs import Env

CORE_APP = 'core'
SETTINGS_MODULE = f'{CORE_APP}.settings'
ROUTES_MODULE = f'{CORE_APP}.routes'
BUILDERS_MODULE = f'{CORE_APP}.builders'
BUILD_DIR = '.build'
ASSETS_DIR = 'assets'

ALEMBIC_INI_PATH = Path(__file__).parent / 'alembic.ini'
MIGRATIONS_DIR = 'migrations'

env = Env()

ROOT = env.path('ROOT', None) or Path.cwd()
sys.path.insert(0, str(ROOT))
DEBUG = env.bool('DEBUG', False)

alembic_config = Config(ALEMBIC_INI_PATH)

APPS = [path for path in ROOT.iterdir() if path.is_dir() and not path.name.startswith('_')]
