"""Unit tests of `src/game/sim/enemies/mantis.py`."""

import pytest
from helpers.enemy_steps import run, run_until
from helpers.fakes import FakeContext

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.mantis import MANTIS_DESIGN, Mantis

CFG = VETERAN_CONFIG.mantis


def test_p05_r16_the_mantis_design_has_two_arm_joints_and_two_blade_parts() -> None:
    assert len(MANTIS_DESIGN.parts) == 2
    assert set(MANTIS_DESIGN.joints.keys()) == {"left-shoulder", "right-shoulder"}


def test_p05_r16_a_mantis_comes_down_to_its_stop_height_and_stays_for_its_time() -> None:
    ctx = FakeContext()
    mantis = Mantis(200, 500, 300)
    run_until(mantis, ctx, lambda: mantis.state == "stay", limit=30.0)
    assert mantis.y == pytest.approx(300)
    run(mantis, ctx, CFG.stay / 2)
    assert mantis.state == "stay"


def test_p05_r16_a_mantis_leaves_downward_once_it_has_stayed() -> None:
    ctx = FakeContext()
    mantis = Mantis(200, 300, 300)
    run_until(mantis, ctx, lambda: mantis.state == "exit", limit=60.0)
    assert mantis.charge == 0
    y = mantis.y
    run(mantis, ctx, 1.0)
    assert mantis.y < y


def test_p05_r16_while_it_stays_its_arms_and_head_fire() -> None:
    ctx = FakeContext()
    mantis = Mantis(200, 300, 300)
    run_until(mantis, ctx, lambda: mantis.state == "stay", limit=10.0)
    run(mantis, ctx, 3.0)
    assert ctx.bullets, "the arms' and head's bullets"
