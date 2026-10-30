"""Unit tests of `src/game/sim/enemies/weaver.py`."""

import math

import pytest
from helpers.enemy_steps import run
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.weaver import Weaver

CFG = ENEMY_CONFIG.weaver


def test_p05_r05_the_sway_is_a_sine_of_the_distance_come_down() -> None:
    assert Weaver.sway_at(200, 0) == pytest.approx(200)
    quarter = CFG.wavelength / 4
    assert Weaver.sway_at(200, quarter) == pytest.approx(200 + CFG.amplitude)


def test_p05_r05_a_weaver_sways_side_to_side_as_it_comes_down() -> None:
    weaver = Weaver(200, 500)
    run(weaver, FakeContext(), 2.0)
    assert weaver.y < 500
    assert weaver.x == pytest.approx(Weaver.sway_at(200, 500 - weaver.y), rel=1e-9)


def test_p05_r05_a_weaver_fires_a_pair_of_aimed_bullets_each_fire_interval() -> None:
    ctx = FakeContext()
    weaver = Weaver(200, 300)
    run(weaver, ctx, 4.5)
    assert len(ctx.bullets) >= 2 * 2
    assert all(spec is CFG.bullet for *_, spec in ctx.bullets)


def test_p05_r05_a_weaver_heads_down_while_it_sways() -> None:
    weaver = Weaver(200, 500)
    run(weaver, FakeContext(), 0.3)
    assert abs(weaver.heading) <= math.pi
