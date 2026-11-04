# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/hive.py`."""

import math

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.sim.enemies.hive import CFG, Hive
from game.sim.enemies.splitter import Splitter
from game.sim.enemy_kinds import ENEMY_KINDS

KIND = next(kind for kind in ENEMY_KINDS if kind.id == "hive")


def test_enm_hive_08_the_kind_spawns_live_enemies_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert enemies
    for enemy in enemies:
        assert enemy.health > 0
        assert math.isfinite(enemy.x)
        assert math.isfinite(enemy.y)


def test_enm_hive_08_a_spawned_enemy_moves_and_stays_finite_over_a_long_run() -> None:
    ctx = FakeContext()
    enemy = KIND.spawn(area(width=400, height=600))[0]
    start = (enemy.x, enemy.y)
    run(enemy, ctx, 8.0)
    assert math.isfinite(enemy.x)
    assert math.isfinite(enemy.y)
    assert (enemy.x, enemy.y) != start


def test_enm_hive_09_the_hive_launches_a_splitter_from_its_hatch_every_six_seconds() -> None:
    ctx = FakeContext()
    hive = Hive(200, 500)
    run(hive, ctx, 2.1)
    assert len(ctx.spawned) == 1
    splitter = ctx.spawned[0]
    assert isinstance(splitter, Splitter)
    assert (splitter.x, splitter.y) == pytest.approx(hive.hatch(ctx), abs=5)
    assert splitter.state == "enter"
    assert CFG.launchInterval == 6
    run(hive, ctx, 5.0)
    assert len(ctx.spawned) == 1
    run(hive, ctx, 1.0)
    assert len(ctx.spawned) == 2


def test_enm_hive_09_the_launched_splitter_stops_a_launch_drop_below_the_hatch() -> None:
    ctx = FakeContext()
    hive = Hive(200, 500)
    run(hive, ctx, 2.1)
    splitter = ctx.spawned[0]
    launched_y = splitter.y
    run_until(splitter, ctx, lambda: splitter.state == "aim", limit=5.0)
    assert splitter.y == pytest.approx(launched_y - CFG.launchDrop, abs=1)


def test_enm_hive_10_the_hive_still_fires_rings_of_bullets() -> None:
    ctx = FakeContext()
    run(Hive(200, 500), ctx, 1.1)
    assert len(ctx.bullets) == CFG.ringCount


def test_enm_hive_11_below_thirty_percent_it_launches_and_fires_nothing() -> None:
    ctx = FakeContext()
    hive = Hive(200, 100)
    run(hive, ctx, 8.0)
    assert ctx.spawned == []
    assert ctx.bullets == []
    assert hive.charge == 0
