# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/scout.py`."""

import math

import pytest
from helpers.enemy_steps import STEP, run
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.scout import Scout

CFG = ENEMY_CONFIG.scout


def test_enm_scout_05_a_scout_flies_straight_down_at_its_speed() -> None:
    scout = Scout(200, 500)
    run(scout, FakeContext(), 1.0)
    assert scout.x == 200
    assert scout.y == pytest.approx(500 - CFG.speed, rel=1e-6)


def test_enm_scout_06_a_scout_fires_an_aimed_bullet_each_fire_interval_on_the_playfield() -> None:
    ctx = FakeContext()
    scout = Scout(200, 560)
    run(scout, ctx, 6.0)
    assert len(ctx.bullets) >= 3
    assert all(spec is CFG.bullet for *_, spec in ctx.bullets)


def test_enm_15_a_scout_above_the_playfield_does_not_fire() -> None:
    """Also ENM-SCOUT-06: it fires only over the playfield."""
    ctx = FakeContext()
    scout = Scout(200, 700)
    run(scout, ctx, 0.5)
    assert ctx.bullets == []


def test_enm_23_a_scout_charges_towards_its_next_shot() -> None:
    scout = Scout(200, 300)
    run(scout, FakeContext(), 0.5)
    assert 0 <= scout.charge <= 1


def test_wpn_02_a_due_shot_waits_for_the_gun_to_turn_to_the_player() -> None:
    """Also ENM-SCOUT-06: the player behind it, the gun needs over a second to come round."""
    ctx = FakeContext()
    ctx.player_y = 590.0
    scout = Scout(200, 300)
    run(scout, ctx, CFG.firstShot + 0.1)
    assert ctx.bullets == []
    run(scout, ctx, 180 / CFG.turret.turnDeg)
    assert len(ctx.bullets) == 1
    _x, _y, heading, _spec = ctx.bullets[0]
    # Up the screen, behind it, within its barrel's aim.
    assert math.cos(heading) > math.cos(math.radians(6))


def test_wpn_01_a_scout_without_its_turret_fires_at_the_player_from_its_muzzle() -> None:
    ctx = FakeContext()
    scout = Scout(200, 300)
    scout.turret = None
    while not ctx.bullets:
        run(scout, ctx, STEP)
    assert len(ctx.bullets) == 1
    x, y, heading, _spec = ctx.bullets[0]
    tip = scout.place(scout.barrels[0].muzzle)
    assert (x, y) == pytest.approx((tip.x, tip.y))
    assert heading == pytest.approx(math.atan2(ctx.player_x - x, ctx.player_y - y))


def test_enm_scout_06_a_shot_before_the_scout_has_flown_fires_nothing() -> None:
    ctx = FakeContext()
    scout = Scout(200, 300)
    scout._fire(200, 300, 0)
    assert ctx.bullets == []
