"""Unit tests of `src/game/sim/enemies/juggernaut.py`."""

import pytest
from helpers.enemy_steps import run, run_until
from helpers.fakes import FakeContext

from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.juggernaut import Juggernaut

BROKEN_JOINTS = pytest.mark.xfail(
    strict=True,
    raises=TypeError,
    reason="BUG: enemies_elite joints are config records (camelCase `amplitudeDeg`), read by "
    "core's BossJoints as `amplitude_deg`: None under CPython (NaN angles in the browser)",
)

CFG = ELITE_CONFIG.juggernaut


@BROKEN_JOINTS
def test_p05_r22_a_juggernaut_comes_down_to_its_stop_height_then_drifts() -> None:
    ctx = FakeContext()
    jug = Juggernaut(200, 500, 300)
    run_until(jug, ctx, lambda: jug.state == "drift", limit=30.0)
    assert jug.y == pytest.approx(300)
    run(jug, ctx, 1.0)
    assert jug.state == "drift"
    assert jug.x != pytest.approx(200)


@BROKEN_JOINTS
def test_p05_r22_a_juggernaut_leaves_downward_after_it_has_drifted_for_its_stay() -> None:
    ctx = FakeContext()
    jug = Juggernaut(200, 300, 300)
    run_until(jug, ctx, lambda: jug.state == "exit", limit=30.0)
    y = jug.y
    run(jug, ctx, 1.0)
    assert jug.y < y


@BROKEN_JOINTS
def test_p05_r22_a_juggernaut_fires_its_spread_from_the_core_when_on_the_playfield() -> None:
    ctx = FakeContext()
    jug = Juggernaut(200, 300, 300)
    run(jug, ctx, 3.0)
    assert len(ctx.bullets) >= CFG.spreadCount
