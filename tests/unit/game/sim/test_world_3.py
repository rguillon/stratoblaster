# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/world_3.py`."""

from game.sim.world_3 import WORLD_3


def test_world_3_is_five_levels_in_order() -> None:
    """WLD-3-01."""
    assert [level.id for level in WORLD_3] == ["3-1", "3-2", "3-3", "3-4", "3-5"]


def test_each_level_of_world_3_has_waves_bosses_and_a_run_out() -> None:
    """Its two bosses (WLD-3-19) and its runout.

    Runout: LVL-3-1-08, LVL-3-2-08, LVL-3-3-08, LVL-3-4-08, LVL-3-5-08.
    """
    for level in WORLD_3:
        assert level.waves
        assert len(level.bosses) == 2
        assert level.runout >= 0
