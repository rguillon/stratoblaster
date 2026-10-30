"""Unit tests of `src/game/sim/world_1.py`."""

from game.sim.world_1 import WORLD_1


def test_world_1_is_five_levels_in_order() -> None:
    assert [level.id for level in WORLD_1] == ["1-1", "1-2", "1-3", "1-4", "1-5"]


def test_each_level_of_world_1_has_waves_bosses_and_a_run_out() -> None:
    for level in WORLD_1:
        assert level.waves
        assert len(level.bosses) == 2
        assert level.runout >= 0
