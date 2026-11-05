# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/hydra.py`."""

import math
from typing import Any

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.sim.enemies.hydra import CFG, Hydra
from game.sim.enemy_kinds import ENEMY_KINDS

KIND = next(kind for kind in ENEMY_KINDS if kind.id == "hydra")

# The Hydra's necks are config joints (camelCase `amplitudeDeg`): `game/sim/joints.py` maps them to
# core's `JointSwing.amplitude_deg`, so they swing alike in both runtimes.


def test_enm_hydra_07_the_kind_spawns_live_enemies_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert enemies
    for enemy in enemies:
        assert enemy.health > 0
        assert math.isfinite(enemy.x)
        assert math.isfinite(enemy.y)
        assert enemy.y >= 600 or enemy.y <= 600


def test_enm_hydra_07_a_spawned_enemy_moves_and_stays_finite_over_a_long_run() -> None:
    ctx = FakeContext()
    enemy = KIND.spawn(area(width=400, height=600))[0]
    start = (enemy.x, enemy.y)
    run(enemy, ctx, 8.0)
    assert math.isfinite(enemy.x)
    assert math.isfinite(enemy.y)
    assert (enemy.x, enemy.y) != start


class _Eyes(FakeContext):
    """Records which head of `hydra` each bullet leaves from (its gun's tip)."""

    def __init__(self, hydra: Hydra) -> None:
        super().__init__()
        self.hydra = hydra
        self.heads: list[str] = []

    def fire_bullet(self, x: float, y: float, heading: float, spec: Any) -> None:
        super().fire_bullet(x, y, heading, spec)
        for head in CFG.heads:
            part = self.hydra.part(head.id)
            tip = self.seen(part.place(head.muzzle)) if part is not None else None
            # One entry per burst.
            fresh = not self.heads or self.heads[-1] != head.id
            if tip is not None and (tip.x, tip.y) == (x, y) and fresh:
                self.heads.append(head.id)


def test_enm_hydra_08_a_hydra_stays_its_time_then_leaves_downward() -> None:
    ctx = FakeContext()
    hydra = Hydra(200, 450, 450)
    run_until(hydra, ctx, lambda: hydra.state == "exit", limit=30.0)
    assert hydra.age == pytest.approx(CFG.stay, abs=0.05)
    y = hydra.y
    run(hydra, ctx, 1.0)
    assert hydra.y == pytest.approx(y - CFG.exitSpeed)


def test_enm_hydra_09_a_head_fires_a_burst_of_bullets_along_itself_not_missiles() -> None:
    """WPN-01, WPN-03: from its gun's tip, along the head as its neck is turned, recoiling."""
    ctx = FakeContext()
    hydra = Hydra(200, 450, 450)
    while len(ctx.bullets) < CFG.burstCount and hydra.age < 3:
        seen = len(ctx.bullets)
        run(hydra, ctx, 1 / 60)
        for x, y, heading, spec in ctx.bullets[seen:]:
            # The head whose gun just fired.
            fired = [i for i, b in enumerate(hydra.barrels) if b.fired_at == hydra.age]
            assert len(fired) == 1
            head = CFG.heads[fired[0]]
            tip = ctx.seen(hydra.part(head.id).place(head.muzzle))
            assert (x, y) == pytest.approx((tip.x, tip.y))
            assert heading == pytest.approx(
                hydra.heading + head.aim + hydra.joints.angle(head.joint)
            )
            assert spec is CFG.bullet
    assert len(ctx.bullets) == CFG.burstCount
    assert ctx.missiles == []


def test_enm_hydra_09_the_heads_left_fire_in_turn() -> None:
    hydra = Hydra(200, 450, 450)
    ctx = _Eyes(hydra)
    hydra.part("head-left").health = 0
    run(hydra, ctx, 2.2)  # shots at 0.5, 1.3 and 2.1 s
    assert ctx.heads == ["head-middle", "head-right", "head-middle"]


def test_enm_hydra_10_with_every_head_gone_it_no_longer_fires() -> None:
    ctx = FakeContext()
    hydra = Hydra(200, 450, 450)
    for head in CFG.heads:
        hydra.part(head.id).health = 0
    run(hydra, ctx, 2.0)
    assert ctx.missiles == []
    assert ctx.bullets == []
    assert len(ctx.broken) == len(CFG.heads)
    assert hydra.health > 0


def test_enm_hydra_10_a_head_shot_off_mid_burst_fires_the_rest_of_it_no_more() -> None:
    """WPN-01: the burst's bullets leave from the head's gun; with the head gone, none leaves."""
    ctx = FakeContext()
    hydra = Hydra(200, 450, 450)
    while not ctx.bullets:
        run(hydra, ctx, 1 / 60)
    assert len(ctx.bullets) == 1
    fired = next(i for i, b in enumerate(hydra.barrels) if b.fired_at is not None)
    hydra.part(CFG.heads[fired].id).health = 0
    # The rest of the burst is due within this time, the next head's burst after it.
    run(hydra, ctx, CFG.burstGap * CFG.burstCount)
    assert len(ctx.bullets) == 1
    assert len(ctx.broken) == 1
