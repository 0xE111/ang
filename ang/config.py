import sys
from pathlib import Path

from environs import Env


env = Env()
root = env.path('ROOT', None) or Path.cwd()

sys.path.insert(0, str(root))


def get_apps() -> list[Path]:
    return [path for path in root.iterdir() if path.is_dir() and not path.name.startswith('_')]
