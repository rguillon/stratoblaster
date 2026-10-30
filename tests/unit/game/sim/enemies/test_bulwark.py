"""Unit tests of `src/game/sim/enemies/bulwark.py`."""

import pytest
from helpers.enemy_steps import run, run_until
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.bulwark import Bulwark

CFG = ENEMY_CONFIG.bulwark


def test_p05_r09_a_bulwark_comes_down_to_its_stop_height_then_drifts() -> None:
    ctx = FakeContext()
    bulwark = Bulwark(200, 700, 300)
    run_until(bulwark, ctx, lambda: bulwark.state == "drift", limit=30.0)
    assert bulwark.y == pytest.approx(300)


def test_p05_r09_a_bulwark_leaves_downward_when_its_drift_is_over() -> None:
    ctx = FakeContext()
    bulwark = Bulwark(200, 300, 300)
    run_until(bulwark, ctx, lambda: bulwark.state == "exit", limit=60.0)
    y = bulwark.y
    run(bulwark, ctx, 1.0)
    assert bulwark.y == pytest.approx(y - CFG.exitSpeed, rel=1e-2)
