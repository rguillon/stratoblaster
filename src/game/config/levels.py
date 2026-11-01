# Copyright (c) 2026 Renaud Guillon
"""Level grid of the first release.

Vision: 4 worlds of 5 levels (UI-LEVEL-01; the rows of WLD-1-02, WLD-3-01, WLD-4-01); World 5 was
dropped. The levels that exist can all be played, in any order (UI-LEVEL-03); any other would stay
locked.
"""

from game.config.record import record

LEVELS_CONFIG = record({
    "worlds": 4,
    "levelsPerWorld": 5,
})
