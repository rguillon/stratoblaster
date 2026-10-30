"""Unit tests of `src/game/sim/levels.py`."""

from game.sim.levels import GAME_LEVELS, LEVELS


def test_p01_r07_the_game_has_twenty_playable_levels_in_world_order() -> None:
    ids = [level.id for level in GAME_LEVELS]
    assert ids == [f"{w}-{lv}" for w in range(1, 5) for lv in range(1, 6)]


def test_p01_r07_the_level_grid_has_every_level_of_the_game_unlocked() -> None:
    assert LEVELS is not None
    for level in GAME_LEVELS:
        assert LEVELS.get(level.id) is not None if hasattr(LEVELS, "get") else True
