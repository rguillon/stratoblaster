# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/hatchery.py`."""

import pytest
from helpers.enemy_steps import area, run
from helpers.fakes import FakeContext

from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.sim.enemies.hatchery import Hatchery
from game.sim.enemies.wasp import Wasp
from game.sim.enemy_kinds import ENEMY_KINDS

CFG = HATCHERY_CONFIG
KIND = next(kind for kind in ENEMY_KINDS if kind.id == "hatchery")


def test_enm_hatchery_05_the_kind_spawns_a_live_hatchery_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert len(enemies) == 1
    assert isinstance(enemies[0], Hatchery)
    assert enemies[0].health > 0
    assert enemies[0].y > 600


def test_enm_hatchery_05_it_descends_straight_down_slowly() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 500)
    run(hatchery, ctx, 1.0)
    assert hatchery.x == 200
    assert hatchery.y == pytest.approx(500 - CFG.speed, rel=1e-2)


def test_enm_hatchery_06_it_never_fires() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 580)
    run(hatchery, ctx, 20.0)
    assert ctx.bullets == []
    assert ctx.missiles == []
    assert ctx.lasers == []


def test_enm_hatchery_07_it_launches_a_group_of_three_wasps_from_its_hatch() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 580)
    run(hatchery, ctx, CFG.firstLaunch + 0.05)
    assert len(ctx.spawned) == 3
    assert all(isinstance(enemy, Wasp) for enemy in ctx.spawned)
    xs = sorted(enemy.x for enemy in ctx.spawned)
    assert xs[0] < 200 < xs[2]
    # Out of the hatch, towards the player's side of its centre.
    assert all(enemy.y < hatchery.y for enemy in ctx.spawned)


def test_enm_hatchery_07_it_launches_again_every_interval() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 590)
    run(hatchery, ctx, CFG.firstLaunch + 0.05)
    assert len(ctx.spawned) == 3
    run(hatchery, ctx, CFG.launchInterval)
    assert len(ctx.spawned) == 6


def test_enm_hatchery_03_its_hatch_charges_towards_the_next_launch() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 590)
    run(hatchery, ctx, CFG.firstLaunch + 0.05)
    low = hatchery.charge
    run(hatchery, ctx, CFG.launchInterval / 2)
    assert hatchery.charge > low


def test_enm_hatchery_08_it_does_not_launch_while_above_the_playfield() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 700)
    run(hatchery, ctx, 3.0)
    assert ctx.spawned == []
    assert hatchery.charge == 0


def test_enm_hatchery_08_it_stops_launching_low_on_the_screen() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, CFG.lastLaunchFraction * 600 - 1)
    run(hatchery, ctx, CFG.firstLaunch + 1.0)
    assert ctx.spawned == []
    assert hatchery.charge == 0


def test_enm_hatchery_09_it_has_400_health_and_scores_700() -> None:
    hatchery = Hatchery(200, 580)
    assert hatchery.health == 400
    assert hatchery.points == 700
    assert hatchery.model == "hatchery"
