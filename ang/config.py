import sys
from importlib import import_module
from pathlib import Path

from environs import Env


env = Env()
root = env.path('ANG_ROOT', None) or Path.cwd()

sys.path.insert(0, str(root))
settings = import_module('settings')
