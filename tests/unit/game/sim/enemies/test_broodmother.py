# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/broodmother.py`."""

import math

import pytest
from helpers.enemy_steps import area, run
from helpers.fakes import FakeContext

from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_tiers import ENEMY_TIERS, tier_of
from game.sim.enemies.broodmother import Broodmother
from game.sim.enemies.phantom import Phantom
from game.sim.enemy_kinds import ENEMY_KINDS
from game.view.enemies.enemy_bindings import ENEMY_BINDINGS

CFG = BROODMOTHER_CONFIG
KIND = next(kind for kind in ENEMY_KINDS if kind.id == "broodmother")


def test_enm_broodmother_06_the_kind_spawns_one_live_broodmother_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert len(enemies) == 1
    assert isinstance(enemies[0], Broodmother)
    assert enemies[0].y > 600
    assert enemies[0].health > 0
    assert math.isfinite(enemies[0].x)


def test_enm_broodmother_06_it_descends_straight_down_and_never_shoots() -> None:
    ctx = FakeContext()
    mother = Broodmother(200, 700)
    run(mother, ctx, 10.0)
    assert mother.x == 200
    assert mother.y == pytest.approx(700 - CFG.speed * 10)
    assert (ctx.bullets, ctx.missiles, ctx.lasers) == ([], [], [])


def test_enm_broodmother_07_it_launches_one_phantom_every_7_seconds_from_its_hatch() -> None:
    ctx = FakeContext()
    mother = Broodmother(200, 590)
    run(mother, ctx, CFG.firstLaunch + 0.1)
    assert len(ctx.spawned) == 1
    phantom = ctx.spawned[0]
    assert isinstance(phantom, Phantom)
    # It comes out of the hatch on the belly, below the centre, and drops from there.
    assert phantom.x == pytest.approx(200 + CFG.port[0])
    assert phantom.y < mother.y
    assert phantom.stop_y == pytest.approx(phantom.y - CFG.launchDrop, abs=CFG.speed * 0.2)
    run(mother, ctx, CFG.launchInterval - 0.2)
    assert len(ctx.spawned) == 1
    run(mother, ctx, 0.3)
    assert len(ctx.spawned) == 2
    assert CFG.launchInterval == 7


def test_enm_broodmother_03_its_charge_rises_towards_each_launch_then_resets() -> None:
    ctx = FakeContext()
    mother = Broodmother(200, 590)
    run(mother, ctx, CFG.firstLaunch / 2)
    assert 0.2 < mother.charge < 0.9
    before = mother.charge
    run(mother, ctx, CFG.firstLaunch / 4)
    assert mother.charge > before
    run(mother, ctx, CFG.firstLaunch)
    assert mother.charge < before


def test_enm_broodmother_07_it_does_not_launch_or_charge_before_it_is_over_the_playfield() -> None:
    ctx = FakeContext()
    mother = Broodmother(200, 700)
    run(mother, ctx, 1.0)
    assert ctx.spawned == []
    assert mother.charge == 0


def test_enm_broodmother_09_it_stops_launching_in_the_lower_part_of_the_screen() -> None:
    ctx = FakeContext()
    mother = Broodmother(200, CFG.lastFraction * 600 - 1)
    run(mother, ctx, CFG.firstLaunch + CFG.launchInterval)
    assert ctx.spawned == []
    assert mother.charge == 0


def test_enm_broodmother_08_the_phantoms_model_is_built_with_every_levels_models() -> None:
    children = set(ENEMY_BINDINGS.child_models)
    assert "phantom" in children
    assert "phantom" in ENEMY_BINDINGS.models


def test_enm_broodmother_11_it_has_700_health_and_scores_1200_points() -> None:
    mother = Broodmother(200, 700)
    assert mother.health == 700
    assert mother.points == 1200
    assert CFG.size == 2


def test_enm_broodmother_10_it_is_a_tier_3_kind_in_its_tiers_neon() -> None:
    assert tier_of("broodmother") == 3
    assert ENEMY_TIERS["3"].kinds.carrier == "broodmother"
    assert ENEMY_LOOK.neon.broodmother == ENEMY_TIERS["3"].neon
