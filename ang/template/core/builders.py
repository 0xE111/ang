from core.settings import STATIC_DIR

from ang.builders import Clear, MoveTo, SkipInternalFiles


BUILDERS = [
    SkipInternalFiles(),
    Clear(STATIC_DIR),
    MoveTo(STATIC_DIR),
]
