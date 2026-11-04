# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/strafer.py`."""

import math

import pytest
from helpers.enemy_steps import STEP, run
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.strafer import Strafer

CFG = ENEMY_CONFIG.strafer


def test_enm_strafer_05_a_strafer_from_the_left_crosses_to_the_right_and_faces_the_side() -> None:
    strafer = Strafer(-10, 100, "left")
    run(strafer, FakeContext(), 1.0)
    assert strafer.x == pytest.approx(-10 + CFG.speed, rel=1e-6)
    assert strafer.heading == pytest.approx(math.pi / 2)


def test_enm_strafer_05_a_strafer_from_the_right_crosses_to_the_left() -> None:
    strafer = Strafer(410, 100, "right")
    run(strafer, FakeContext(), 1.0)
    assert strafer.x == pytest.approx(410 - CFG.speed, rel=1e-6)
    assert strafer.heading == pytest.approx(-math.pi / 2)


def test_enm_strafer_06_a_strafer_fires_a_fan_of_bullets_each_fire_interval() -> None:
    ctx = FakeContext()
    strafer = Strafer(200, 100, "left")
    run(strafer, ctx, 2.0)
    shots = len(ctx.bullets)
    assert shots > 0
    assert shots % CFG.fanCount == 0
    headings = sorted({round(h, 3) for _, _, h, _ in ctx.bullets})
    assert len(headings) == CFG.fanCount


def test_wpn_04_a_strafer_has_three_barrels_on_each_side() -> None:
    strafer = Strafer(200, 100, "left")
    assert len(strafer.barrels) == 6
    assert sorted(round(math.degrees(b.angle or 0)) for b in strafer.barrels) == [
        -105,
        -90,
        -75,
        75,
        90,
        105,
    ]


def test_wpn_01_each_bullet_leaves_its_barrel_tip_along_the_barrel() -> None:
    ctx = FakeContext()
    strafer = Strafer(200, 100, "left")
    # Step until the first volley leaves: the tips are compared where the Strafer is at that step.
    while not ctx.bullets:
        run(strafer, ctx, STEP)
    assert len(ctx.bullets) == 3
    tips = [strafer.place(b.muzzle) for b in strafer.barrels]
    for x, y, heading, _ in ctx.bullets:
        # One of the barrels' tips, and the way that barrel points.
        owners = [
            b
            for b, tip in zip(strafer.barrels, tips, strict=True)
            if abs(tip.x - x) < 0.01
            and abs(tip.y - y) < 0.01
            and abs(strafer.heading + (b.angle or 0) - heading) < 1e-4
        ]
        assert len(owners) == 1


def test_wpn_03_the_barrels_that_fired_recoil_and_the_others_do_not() -> None:
    ctx = FakeContext()
    strafer = Strafer(200, 100, "left")
    run(strafer, ctx, 1.6)
    recoils = [b.recoil_at(strafer.age) for b in strafer.barrels]
    assert sum(1 for r in recoils if r > 0) <= 3
    assert all(0 <= r <= 1 for r in recoils)
