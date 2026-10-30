"""Unit tests of `src/game/sim/bosses/boss_launches.py`."""

from helpers.enemy_steps import run
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.bosses.boss_launches import launch_fire
from game.sim.enemies.gnat import Gnat
from game.sim.enemies.hornet import Hornet


def test_p07_r05_gnats_leave_a_hangar_in_a_group_of_the_asked_count() -> None:
    gnats = launch_fire("gnats", 3, 1)(100, 200)
    assert len(gnats) == 3
    assert all(isinstance(g, Gnat) for g in gnats)
    delays = [g.delay for g in gnats]
    assert delays == [i * ENEMY_CONFIG.gnat.groupDelay for i in range(3)]


def test_p07_r05_gnats_go_out_to_the_side_the_hangar_is_on() -> None:
    right = launch_fire("gnats", 1, 1)(100, 200)[0]
    left = launch_fire("gnats", 1, -1)(100, 200)[0]
    run(right, FakeContext(), 1.0)
    run(left, FakeContext(), 1.0)
    assert right.x > 100 > left.x


def test_p07_r05_hornets_leave_a_bay_side_by_side_centred_on_the_launch_point() -> None:
    hornets = launch_fire("hornets", 3, 1)(200, 300)
    assert len(hornets) == 3
    assert all(isinstance(h, Hornet) for h in hornets)
    xs = [h.x for h in hornets]
    assert xs == [200 - 14, 200, 200 + 14]


def test_p07_r05_a_side_of_zero_still_sends_gnats_out_to_the_right() -> None:
    gnat = launch_fire("gnats", 1, 0)(100, 200)[0]
    run(gnat, FakeContext(), 1.0)
    assert gnat.x > 100
