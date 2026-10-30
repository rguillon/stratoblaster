"""This game's levels (P01-R07, P06-R01), ported from `game/sim/levels.ts`."""

from core.content.game_level import GameLevel
from core.content.level_catalog import build_level_grid
from game.config.levels import LEVELS_CONFIG
from game.sim.world_1 import WORLD_1
from game.sim.world_2 import WORLD_2
from game.sim.world_3 import WORLD_3
from game.sim.world_4 import WORLD_4


def _all_levels() -> list[GameLevel]:
    """Every playable level of this game, Worlds 1 to 4 in order (P06, P08, P09, P10)."""
    levels: list[GameLevel] = []
    levels.extend(WORLD_1)
    levels.extend(WORLD_2)
    levels.extend(WORLD_3)
    levels.extend(WORLD_4)
    return levels


# Every playable level of this game, Worlds 1 to 4 in order (P06, P08, P09, P10).
GAME_LEVELS = _all_levels()

# This game's levels (P01-R07): every level that exists is unlocked (P06-R01).
LEVELS = build_level_grid(
    LEVELS_CONFIG.worlds,
    LEVELS_CONFIG.levelsPerWorld,
    [level.id for level in GAME_LEVELS],
)
