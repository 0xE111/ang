from core.settings import STATIC_DIR

from ang.build import Clear, MoveTo, SkipInternalFiles


BUILD_ACTIONS = [
    SkipInternalFiles(),
    Clear(STATIC_DIR),
    MoveTo(STATIC_DIR),
]
