import sys
from pathlib import Path

from alembic.config import Config
from environs import Env

CORE_APP = 'core'
SETTINGS_MODULE = 'settings'
ROUTES_MODULE = 'routes'
BUILDERS_MODULE = 'builders'
BUILD_DIR = '.build'
ASSETS_DIR = 'assets'

ALEMBIC_INI_PATH = Path(__file__).parent / 'alembic.ini'
MIGRATIONS_DIR = 'migrations'

env = Env()

ROOT = env.path('ROOT', None) or Path.cwd()
sys.path.insert(0, str(ROOT))

alembic_config = Config(ALEMBIC_INI_PATH)
# breakpoint()


APPS = [path for path in ROOT.iterdir() if path.is_dir() and not path.name.startswith('_')]

# def get_apps() -> list[Path]:
#     return [path for path in root.iterdir() if path.is_dir() and not path.name.startswith('_')]
