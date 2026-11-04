# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/mortar.py`."""

import math

import pytest
from helpers.enemy_steps import area, run
from helpers.fakes import FakeContext

from game.sim.enemies.mortar import CFG, Mortar, mortar_missile
from game.sim.enemy_kinds import ENEMY_KINDS

KIND = next(kind for kind in ENEMY_KINDS if kind.id == "mortar")


def test_enm_mortar_07_the_kind_spawns_live_enemies_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert enemies
    for enemy in enemies:
        assert enemy.health > 0
        assert math.isfinite(enemy.x)
        assert math.isfinite(enemy.y)


def test_enm_mortar_07_a_spawned_enemy_moves_and_stays_finite_over_a_long_run() -> None:
    ctx = FakeContext()
    enemy = KIND.spawn(area(width=400, height=600))[0]
    start = (enemy.x, enemy.y)
    run(enemy, ctx, 8.0)
    assert math.isfinite(enemy.x)
    assert math.isfinite(enemy.y)
    assert (enemy.x, enemy.y) != start


def test_enm_mortar_08_the_mortar_launches_a_homing_missile_from_its_tube_at_the_player() -> None:
    ctx = FakeContext()
    mortar = Mortar(200, 400)
    run(mortar, ctx, CFG.firstShot + 0.2)
    assert len(ctx.missiles) == 1
    x, y, heading, spec = ctx.missiles[0]
    assert (x, y) == pytest.approx((200, 400 - 40 * CFG.firstShot - 12.5), abs=1)
    # The player is straight below it: the missile starts that way.
    assert heading == pytest.approx(math.pi)
    assert (spec.speed, spec.turn_rate_deg, spec.radius) == (90, 55, 8)
    assert spec.health == CFG.missile.health
    assert ctx.bullets == []


def test_enm_mortar_08_the_mortar_launches_one_missile_every_interval() -> None:
    ctx = FakeContext()
    mortar = Mortar(200, 700)
    run(mortar, ctx, 0.5)
    assert ctx.missiles == []
    mortar.y = 500
    run(mortar, ctx, CFG.firstShot + CFG.fireInterval + 0.2)
    assert len(ctx.missiles) == 2
    assert 0 <= mortar.charge <= 1


def test_enm_mortar_08_a_mortar_outside_the_playfield_launches_nothing() -> None:
    ctx = FakeContext()
    mortar = Mortar(200, 700)
    run(mortar, ctx, 3.0)
    assert ctx.missiles == []


def test_enm_mortar_09_the_missile_bursts_after_its_fuse_into_a_ring_of_bullets() -> None:
    spec = mortar_missile()
    assert spec.burst is not None
    assert spec.burst.after == 2.5
    assert spec.burst.count == 10
    assert spec.burst.bullet.speed == 130
    assert spec.burst.bullet.style == "green"


def test_enm_mortar_10_a_mortar_has_120_hp_and_scores_350_points() -> None:
    mortar = Mortar(200, 400)
    assert mortar.health == 120
    assert mortar.points == 350
