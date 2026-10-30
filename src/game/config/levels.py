"""Level grid of the first release

Vision: 4 worlds of 5 levels; World 5 was dropped. The levels that exist can all be played, in any
order (P06-R01); any other would stay locked.
"""

from game.config.record import record

LEVELS_CONFIG = record(
    {
        "worlds": 4,
        "levelsPerWorld": 5,
    }
)
