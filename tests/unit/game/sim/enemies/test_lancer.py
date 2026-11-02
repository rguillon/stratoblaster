# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/lancer.py`."""

import pytest
from helpers.enemy_steps import run, run_until
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.lancer import Lancer, LancerBeam

CFG = ENEMY_CONFIG.lancer


def test_enm_lancer_05_a_lancer_comes_in_stops_at_its_height_and_fires_its_laser() -> None:
    """Also ENM-LANCER-06: its laser."""
    ctx = FakeContext()
    lancer = Lancer(200, 500, 300)
    run_until(lancer, ctx, lambda: lancer.state == "attack", limit=10.0)
    assert lancer.y == pytest.approx(300)
    assert len(ctx.lasers) == 1
    owner, spec = ctx.lasers[0]
    assert isinstance(owner, LancerBeam)
    assert spec is CFG.laser


def test_enm_lancer_03_a_lancer_charges_during_its_warning_and_holds_still() -> None:
    """Also ENM-LANCER-06: it holds still."""
    ctx = FakeContext()
    lancer = Lancer(200, 300, 300)
    run_until(lancer, ctx, lambda: lancer.state == "attack", limit=10.0)
    run(lancer, ctx, 0.5)
    assert lancer.y == pytest.approx(300)
    assert lancer.charge == pytest.approx(0.5, abs=0.02)


def test_enm_lancer_07_a_lancer_backs_away_upward_after_its_laser() -> None:
    ctx = FakeContext()
    lancer = Lancer(200, 300, 300)
    run_until(lancer, ctx, lambda: lancer.state == "exit", limit=10.0)
    assert lancer.state == "exit"
    assert lancer.charge == 0
    run(lancer, ctx, 0.5)
    assert lancer.y == pytest.approx(300 + CFG.exitSpeed * 0.5, rel=1e-2)


def test_enm_lancer_06_the_laser_beam_follows_the_lancers_nose_and_heading() -> None:
    lancer = Lancer(200, 300, 300)
    beam = LancerBeam(lancer, CFG.muzzle)
    assert beam.heading == lancer.heading
    assert beam.gone is False
    assert beam.health == lancer.health
    assert beam.emitter is not None
