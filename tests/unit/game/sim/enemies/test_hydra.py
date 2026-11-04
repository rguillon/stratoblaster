# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/hydra.py`."""

import math
from typing import Any

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
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
    """Records which head of `hydra` each missile leaves from."""

    def __init__(self, hydra: Hydra) -> None:
        super().__init__()
        self.hydra = hydra
        self.heads: list[str] = []

    def fire_missile(self, x: float, y: float, heading: float, spec: Any) -> None:
        super().fire_missile(x, y, heading, spec)
        for head in CFG.heads:
            part = self.hydra.part(head.id)
            eye = self.seen(part.place(head.muzzle)) if part is not None else None
            if eye is not None and (eye.x, eye.y) == (x, y):
                self.heads.append(head.id)


def test_enm_hydra_08_a_hydra_stays_its_time_then_leaves_downward() -> None:
    ctx = FakeContext()
    hydra = Hydra(200, 450, 450)
    run_until(hydra, ctx, lambda: hydra.state == "exit", limit=30.0)
    assert hydra.age == pytest.approx(CFG.stay, abs=0.05)
    y = hydra.y
    run(hydra, ctx, 1.0)
    assert hydra.y == pytest.approx(y - CFG.exitSpeed)


def test_enm_hydra_09_the_heads_launch_homing_missiles_not_bullets() -> None:
    """Also ENM-HYDRA-14: slower than the Rocketeer's, a little slower cadence than before."""
    ctx = FakeContext()
    hydra = Hydra(200, 450, 450)
    run(hydra, ctx, 1.0)
    assert ctx.bullets == []
    assert len(ctx.missiles) == 1
    assert ctx.missiles[0][3].turn_rate_deg == CFG.missile.turnRateDeg
    assert CFG.missile.speed < ENEMY_CONFIG.rocketeer.missile.speed
    assert CFG.headFireInterval > 0.5


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
