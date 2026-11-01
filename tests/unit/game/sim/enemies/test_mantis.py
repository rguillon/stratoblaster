"""Unit tests of `src/game/sim/enemies/mantis.py`."""

import pytest
from helpers.enemy_steps import run, run_until
from helpers.fakes import FakeContext

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.mantis import MANTIS_DESIGN, Mantis

CFG = VETERAN_CONFIG.mantis


def test_enm_mantis_12_the_mantis_design_has_two_arm_joints_and_two_blade_parts() -> None:
    """Also ENM-MANTIS-09: the arms swing on their joints."""
    assert len(MANTIS_DESIGN.parts) == 2
    assert set(MANTIS_DESIGN.joints.keys()) == {"left-shoulder", "right-shoulder"}


def test_enm_mantis_08_a_mantis_comes_down_to_its_stop_height_and_stays_for_its_time() -> None:
    ctx = FakeContext()
    mantis = Mantis(200, 500, 300)
    run_until(mantis, ctx, lambda: mantis.state == "stay", limit=30.0)
    assert mantis.y == pytest.approx(300)
    run(mantis, ctx, CFG.stay / 2)
    assert mantis.state == "stay"


def test_enm_mantis_08_a_mantis_leaves_downward_once_it_has_stayed() -> None:
    """Also ENM-MANTIS-04: its charge lights go out."""
    ctx = FakeContext()
    mantis = Mantis(200, 300, 300)
    run_until(mantis, ctx, lambda: mantis.state == "exit", limit=60.0)
    assert mantis.charge == 0
    y = mantis.y
    run(mantis, ctx, 1.0)
    assert mantis.y < y


def test_enm_mantis_10_while_it_stays_its_arms_and_head_fire() -> None:
    """Also ENM-MANTIS-11: the head's aimed shot."""
    ctx = FakeContext()
    mantis = Mantis(200, 300, 300)
    run_until(mantis, ctx, lambda: mantis.state == "stay", limit=10.0)
    run(mantis, ctx, 3.0)
    assert ctx.bullets, "the arms' and head's bullets"
