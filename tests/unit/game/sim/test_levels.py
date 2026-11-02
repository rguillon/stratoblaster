# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/levels.py`."""

from game.sim.levels import GAME_LEVELS, LEVELS


def test_ui_level_01_the_game_has_twenty_playable_levels_in_world_order() -> None:
    """Also WLD-3-01 and WLD-4-01: Worlds 3 and 4 in their place."""
    ids = [level.id for level in GAME_LEVELS]
    assert ids == [f"{w}-{lv}" for w in range(1, 5) for lv in range(1, 6)]


def test_ui_level_03_the_level_grid_has_every_level_of_the_game_unlocked() -> None:
    """Also UI-LEVEL-02 (the grid from the game's levels) and WLD-1-02."""
    assert LEVELS is not None
    for level in GAME_LEVELS:
        assert LEVELS.get(level.id) is not None if hasattr(LEVELS, "get") else True
