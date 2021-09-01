from ang.builders import SkipInternalFiles, Move
from core.settings import STATIC_DIR


BUILDERS = [
    SkipInternalFiles(),
    Move(destination=STATIC_DIR),
]
