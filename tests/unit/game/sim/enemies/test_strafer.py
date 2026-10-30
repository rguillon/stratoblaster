"""Unit tests of `src/game/sim/enemies/strafer.py`."""

import math

import pytest
from helpers.enemy_steps import run
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.strafer import Strafer

CFG = ENEMY_CONFIG.strafer


def test_p05_r04_a_strafer_from_the_left_crosses_to_the_right_and_faces_the_side() -> None:
    strafer = Strafer(-10, 100, "left")
    run(strafer, FakeContext(), 1.0)
    assert strafer.x == pytest.approx(-10 + CFG.speed, rel=1e-6)
    assert strafer.heading == pytest.approx(math.pi / 2)


def test_p05_r04_a_strafer_from_the_right_crosses_to_the_left() -> None:
    strafer = Strafer(410, 100, "right")
    run(strafer, FakeContext(), 1.0)
    assert strafer.x == pytest.approx(410 - CFG.speed, rel=1e-6)
    assert strafer.heading == pytest.approx(-math.pi / 2)


def test_p05_r04_a_strafer_fires_a_fan_of_bullets_each_fire_interval() -> None:
    ctx = FakeContext()
    strafer = Strafer(200, 100, "left")
    run(strafer, ctx, 2.0)
    shots = len(ctx.bullets)
    assert shots > 0 and shots % CFG.fanCount == 0
    headings = sorted({round(h, 3) for _, _, h, _ in ctx.bullets})
    assert len(headings) == CFG.fanCount
