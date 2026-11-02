# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/juggernaut.py`."""

import pytest
from helpers.enemy_steps import run, run_until
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


def _cannon_bullets(ctx: FakeContext) -> int:
    return sum(1 for bullet in ctx.bullets if bullet[3] is CFG.cannonBullet)


def test_enm_juggernaut_10_each_standing_cannon_fires_its_burst() -> None:
    both = FakeContext()
    run(Juggernaut(200, 300, 300), both, 1.1)  # the first burst, before the core's first spread
    assert _cannon_bullets(both) == 2 * CFG.burstCount
    one = FakeContext()
    jug = Juggernaut(200, 300, 300)
    jug.part("cannon-left").health = 0
    run(jug, one, 1.1)
    assert _cannon_bullets(one) == CFG.burstCount


def test_enm_15_a_juggernaut_above_the_playfield_holds_its_fire() -> None:
    ctx = FakeContext()
    jug = Juggernaut(200, 800, 300)
    run(jug, ctx, 3.0)
    assert jug.y > ctx.height
    assert ctx.bullets == []
