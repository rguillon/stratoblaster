# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/wasp.py`."""

import math

from helpers.enemy_steps import area, run
from helpers.fakes import FakeContext

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.wasp import Wasp
from game.sim.enemy_kinds import ENEMY_KINDS

KIND = next(kind for kind in ENEMY_KINDS if kind.id == "wasp")


def test_enm_wasp_07_the_kind_spawns_live_enemies_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert enemies
    for enemy in enemies:
        assert enemy.health > 0
        assert math.isfinite(enemy.x)
        assert math.isfinite(enemy.y)


def test_enm_wasp_08_a_spawned_enemy_moves_and_stays_finite_over_a_long_run() -> None:
    ctx = FakeContext()
    enemy = KIND.spawn(area(width=400, height=600))[0]
    start = (enemy.x, enemy.y)
    run(enemy, ctx, 8.0)
    assert math.isfinite(enemy.x)
    assert math.isfinite(enemy.y)
    assert (enemy.x, enemy.y) != start


def test_enm_15_a_wasp_off_the_playfield_dives_without_firing() -> None:
    """Also ENM-WASP-09: over the playfield, it fires its fan as the pause ends."""
    off = FakeContext()
    wasp = Wasp(-50, 300, 300)
    run(wasp, off, 1.0)
    assert wasp.state == "dive"
    assert off.bullets == []
    over = FakeContext()
    run(Wasp(200, 300, 300), over, 1.0)
    assert len(over.bullets) == VETERAN_CONFIG.wasp.fanCount
