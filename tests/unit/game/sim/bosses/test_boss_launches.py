# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/bosses/boss_launches.py`."""

from game.sim.bosses.boss_launches import launch_fire
from game.sim.enemies.hornet import Hornet


def test_boss_25_hornets_leave_a_bay_side_by_side_centred_on_the_launch_point() -> None:
    hornets = launch_fire(3)(200, 300)
    assert len(hornets) == 3
    assert all(isinstance(h, Hornet) for h in hornets)
    xs = [h.x for h in hornets]
    assert xs == [200 - 14, 200, 200 + 14]


def test_boss_25_a_bay_launches_the_asked_count_from_the_launch_height() -> None:
    hornets = launch_fire(1)(100, 200)
    assert len(hornets) == 1
    assert (hornets[0].x, hornets[0].y) == (100, 200)
