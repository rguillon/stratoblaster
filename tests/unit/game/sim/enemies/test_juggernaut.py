# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/juggernaut.py`."""

import itertools
import math

import pytest
from helpers.enemy_steps import STEP, run, run_until
from helpers.fakes import FakeContext

from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.juggernaut import Juggernaut

CFG = ELITE_CONFIG.juggernaut


def test_enm_juggernaut_08_a_juggernaut_comes_down_to_its_stop_height_then_drifts() -> None:
    ctx = FakeContext()
    jug = Juggernaut(200, 500, 300)
    run_until(jug, ctx, lambda: jug.state == "drift", limit=30.0)
    assert jug.y == pytest.approx(300)
    run(jug, ctx, 1.0)
    assert jug.state == "drift"
    assert jug.x != pytest.approx(200)


def test_enm_juggernaut_08_a_juggernaut_leaves_downward_after_it_has_drifted_for_its_stay() -> None:
    ctx = FakeContext()
    jug = Juggernaut(200, 300, 300)
    run_until(jug, ctx, lambda: jug.state == "exit", limit=30.0)
    y = jug.y
    run(jug, ctx, 1.0)
    assert jug.y < y


def test_enm_juggernaut_11_a_juggernaut_fires_its_core_spread_on_the_playfield() -> None:
    ctx = FakeContext()
    jug = Juggernaut(200, 300, 300)
    run(jug, ctx, 3.0)
    assert len(ctx.bullets) >= CFG.spreadCount


def test_enm_juggernaut_10_each_standing_launcher_launches_a_missile_along_itself() -> None:
    """WPN-08: from its port, along the launcher as its joint is turned (the Hydra's missiles)."""
    both = FakeContext()
    jug = Juggernaut(200, 300, 300)
    # The first launch, before the core's first spread: compared at the step it leaves.
    while not both.missiles:
        run(jug, both, STEP)
    assert len(both.missiles) == 2
    for (x, y, heading, spec), cannon in zip(both.missiles, CFG.cannons, strict=True):
        tip = both.seen(jug.part(cannon.id).place(cannon.muzzle))
        assert (x, y) == pytest.approx((tip.x, tip.y))
        assert heading == pytest.approx(jug.heading + jug.joints.angle(cannon.joint))
        assert spec.speed == CFG.missile.speed
    one = FakeContext()
    jug = Juggernaut(200, 300, 300)
    jug.part("cannon-left").health = 0
    run(jug, one, 0.85)
    assert len(one.missiles) == 1


def test_enm_15_a_juggernaut_above_the_playfield_holds_its_fire() -> None:
    ctx = FakeContext()
    jug = Juggernaut(200, 800, 300)
    run(jug, ctx, 3.0)
    assert jug.y > ctx.height
    assert ctx.bullets == []


def test_enm_juggernaut_11_the_turret_sweeps_the_spread_one_parallel_barrel_after_the_other() -> (
    None
):
    """WPN-01, WPN-02: each bullet leaves its own barrel's tip, along the turret, a gap apart."""
    ctx = FakeContext()
    jug = Juggernaut(200, 300, 300)
    # Parallel barrels: none has an angle of its own, they turn with the turret.
    assert all(b.angle is None for b in jug.barrels[:7])
    shots: list[tuple[float, float, float, float]] = []
    tips: list[tuple[float, float]] = []
    while len(shots) < CFG.spreadCount and jug.age < 10:
        seen = len(ctx.bullets)
        run(jug, ctx, STEP)
        for x, y, heading, spec in ctx.bullets[seen:]:
            if spec is CFG.cannonBullet:
                continue
            shots.append((jug.age, x, y, heading))
            # The turret's heading, and the tip of the barrel that just kicked.
            assert heading == pytest.approx(jug.heading + jug.turret.aim)
            fired = [b for b in jug.barrels[:7] if b.fired_at == jug.age]
            assert len(fired) == 1
            tip = jug.place(fired[0].muzzle, True)
            tips.append((tip.x, tip.y))
            assert (x, y) == pytest.approx((tip.x, tip.y))
    assert len(shots) == CFG.spreadCount
    # Seven different barrels, a sweep gap or more apart.
    assert len({round(t[0], 4) for t in shots}) == CFG.spreadCount
    for a, b in itertools.pairwise(shots):
        assert b[0] - a[0] >= CFG.sweepGap - 1e-9
    # Still a spread: 9° from one bullet to the next.
    headings = [s[3] for s in shots]
    for a, b in itertools.pairwise(headings):
        assert abs(b - a) == pytest.approx(math.radians(CFG.spreadSpacing))
