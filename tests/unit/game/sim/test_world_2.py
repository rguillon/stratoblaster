"""Unit tests of `src/game/sim/world_2.py`."""

from game.sim.world_2 import WORLD_2


def test_world_2_is_five_levels_in_order() -> None:
    assert [level.id for level in WORLD_2] == ["2-1", "2-2", "2-3", "2-4", "2-5"]


def test_each_level_of_world_2_has_waves_bosses_and_a_run_out() -> None:
    for level in WORLD_2:
        assert level.waves
        assert len(level.bosses) == 2
        assert level.runout >= 0
