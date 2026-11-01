# Copyright (c) 2026 Renaud Guillon
"""The game's levels (UI-LEVEL-02, UI-LEVEL-03)."""

from core.content.game_level import GameLevel
from core.content.level_catalog import build_level_grid
from game.config.levels import LEVELS_CONFIG
from game.sim.world_1 import WORLD_1
from game.sim.world_2 import WORLD_2
from game.sim.world_3 import WORLD_3
from game.sim.world_4 import WORLD_4


def _all_levels() -> list[GameLevel]:
    """Every playable level of this game, Worlds 1 to 4 in order."""
    levels: list[GameLevel] = []
    levels.extend(WORLD_1)
    levels.extend(WORLD_2)
    levels.extend(WORLD_3)
    levels.extend(WORLD_4)
    return levels


# Every playable level of this game, Worlds 1 to 4 in order (WLD-3-01, WLD-4-01).
GAME_LEVELS = _all_levels()

# This game's levels, a row of the level select a world (WLD-1-02, WLD-2-02), from the game's data
# (UI-LEVEL-02): every level that exists is unlocked (UI-LEVEL-03).
LEVELS = build_level_grid(
    LEVELS_CONFIG.worlds,
    LEVELS_CONFIG.levelsPerWorld,
    [level.id for level in GAME_LEVELS],
)
