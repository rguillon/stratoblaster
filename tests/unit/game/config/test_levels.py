"""Unit tests of `src/game/config/levels.py`."""

from helpers.config_checks import LEVEL_IDS, LEVELS_PER_WORLD, WORLDS

from game.config.levels import LEVELS_CONFIG


def test_p06_r01_the_level_grid_is_four_worlds_of_five_levels() -> None:
    assert LEVELS_CONFIG.worlds == len(WORLDS) == 4
    assert LEVELS_CONFIG.levelsPerWorld == LEVELS_PER_WORLD == 5
    assert len(LEVEL_IDS) == LEVELS_CONFIG.worlds * LEVELS_CONFIG.levelsPerWorld
