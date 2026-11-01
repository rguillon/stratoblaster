# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/scissor.py`."""

from typing import Any

import pytest
from helpers.enemy_steps import run, run_until
from helpers.fakes import FakeContext

from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.scissor import ArmBeam, Scissor

CFG = ELITE_CONFIG.scissor


def test_enm_scissor_08_a_scissor_stops_at_its_height_and_warns_with_two_arm_lasers() -> None:
    """Also ENM-SCISSOR-09 (the arms held still) and ENM-SCISSOR-10 (the warning lines)."""
    ctx = FakeContext()
    scissor = Scissor(200, 500, 300)
    run_until(scissor, ctx, lambda: scissor.state == "warn", limit=10.0)
    assert scissor.y == pytest.approx(300)
    assert len(ctx.lasers) == len(CFG.arms)
    assert all(isinstance(owner, ArmBeam) for owner, _ in ctx.lasers)
    assert scissor.swinging is False


def test_enm_scissor_11_the_arms_swing_inward_only_while_the_lasers_fire() -> None:
    """Also ENM-SCISSOR-12: then it leaves."""
    ctx = FakeContext()
    scissor = Scissor(200, 300, 300)
    run_until(scissor, ctx, lambda: scissor.state == "warn", limit=10.0)
    run_until(scissor, ctx, lambda: scissor.state == "fire", limit=5.0)
    assert scissor.swinging is True
    run_until(scissor, ctx, lambda: scissor.state == "exit", limit=10.0)
    assert scissor.swinging is False
    assert scissor.charge == 0


def test_enm_scissor_06_the_warning_charges_up_to_the_end_of_the_warning() -> None:
    ctx = FakeContext()
    scissor = Scissor(200, 300, 300)
    run_until(scissor, ctx, lambda: scissor.state == "warn", limit=10.0)
    run(scissor, ctx, CFG.laser.warningSeconds / 2)
    assert scissor.charge == pytest.approx(0.5, abs=0.02)


def test_enm_scissor_11_the_arm_beam_follows_its_arm() -> None:
    class _Arm:
        x, y, heading, gone, health = 1.0, 2.0, 0.5, False, 9.0

        def place(self, _muzzle: Any) -> Any:
            return (self.x, self.y)

    beam = ArmBeam(_Arm(), CFG.arms[0].muzzle)
    assert beam.heading == 0.5
    assert beam.health == 9.0
    assert beam.gone is False
    assert beam.emitter == (1.0, 2.0)
