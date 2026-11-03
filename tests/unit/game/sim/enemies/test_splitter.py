# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/splitter.py`."""

import math

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.sim.enemies.hornet import Hornet
from game.sim.enemies.splitter import CFG, POD, Splitter
from game.sim.enemy_kinds import ENEMY_KINDS

KIND = next(kind for kind in ENEMY_KINDS if kind.id == "splitter")


def test_enm_splitter_05_the_kind_spawns_one_splitter_above_the_top_edge() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert len(enemies) == 1
    assert isinstance(enemies[0], Splitter)
    assert enemies[0].y >= 600
    assert enemies[0].state == "enter"


def test_enm_splitter_05_a_splitter_is_a_tougher_diver_than_a_hornet() -> None:
    assert CFG.stats.health == 200
    assert CFG.stats.points == 450
    assert CFG.size > 0.7


def test_enm_splitter_06_a_splitter_brakes_aims_then_dives_at_the_player() -> None:
    ctx = FakeContext()
    splitter = Splitter(200, 700, 420)
    run_until(splitter, ctx, lambda: splitter.state == "aim", limit=10.0)
    assert splitter.y == pytest.approx(420)
    run_until(splitter, ctx, lambda: splitter.state == "dive", limit=10.0)
    assert splitter.dive_heading is not None
    y = splitter.y
    run(splitter, ctx, 0.5)
    assert splitter.y < y


def test_enm_splitter_06_a_splitter_never_shoots() -> None:
    ctx = FakeContext()
    run(Splitter(200, 700, 420), ctx, 6.0)
    assert ctx.bullets == []
    assert ctx.missiles == []
    assert ctx.lasers == []


def test_enm_splitter_06_a_splitter_launched_below_its_stop_height_starts_aiming() -> None:
    """The Hive launches it mid-screen (ENM-HIVE-09)."""
    low = Splitter(200, 300, 500)
    run(low, FakeContext(), 0.05)
    assert low.state == "aim"
    assert low.y == 300
    assert Splitter(200, 300, 100).state == "enter"


def test_enm_splitter_07_a_destroyed_splitter_releases_three_pods_round_its_core() -> None:
    ctx = FakeContext()
    splitter = Splitter(200, 300, 100)
    splitter.on_destroyed(ctx)
    assert len(ctx.spawned) == 3
    assert all(isinstance(pod, Hornet) for pod in ctx.spawned)
    headings = sorted(pod.heading % (2 * math.pi) for pod in ctx.spawned)
    assert headings[1] - headings[0] == pytest.approx(2 * math.pi / 3, rel=1e-6)


def test_enm_splitter_08_each_pod_starts_with_its_pause_and_dives() -> None:
    ctx = FakeContext()
    splitter = Splitter(200, 300, 100)
    splitter.on_destroyed(ctx)
    for pod in ctx.spawned:
        assert pod.state == "aim"
        assert pod.health == POD.stats.health
        run(pod, ctx, POD.pause + 0.2)
        assert pod.state == "dive"
    assert ctx.bullets == []


def test_enm_splitter_05_one_that_reaches_the_bottom_just_leaves_without_pods() -> None:
    ctx = FakeContext()
    splitter = Splitter(200, 300, 100)
    run(splitter, ctx, 6.0)
    assert splitter.y < -100
    assert ctx.spawned == []
