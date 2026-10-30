"""Unit tests of `src/game/sim/world_4.py`."""

from game.sim.world_4 import WORLD_4


def test_world_4_is_five_levels_in_order() -> None:
    assert [level.id for level in WORLD_4] == ["4-1", "4-2", "4-3", "4-4", "4-5"]


def test_each_level_of_world_4_has_waves_bosses_and_a_run_out() -> None:
    for level in WORLD_4:
        assert level.waves
        assert len(level.bosses) == 2
        assert level.runout >= 0
