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
    # A warning line first, then the beam (the core reads the snake-case fields).
    assert spec.warning_seconds == CFG.laser.warningSeconds
    assert spec.firing_seconds == CFG.laser.firingSeconds
    assert spec.width == CFG.laser.width
    assert spec.style == CFG.laser.style


def test_enm_lancer_03_a_lancer_charges_during_its_warning_and_holds_still() -> None:
    """Also ENM-LANCER-06: it holds still."""
    ctx = FakeContext()
    lancer = Lancer(200, 300, 300)
    run_until(lancer, ctx, lambda: lancer.state == "attack", limit=10.0)
    run(lancer, ctx, 0.5)
    assert lancer.y == pytest.approx(300)
    assert lancer.charge == pytest.approx(0.5, abs=0.02)


def test_enm_lancer_07_after_its_laser_a_lancer_goes_on_down_to_its_next_stop_and_fires() -> None:
    ctx = FakeContext()
    first = CFG.stopRange[1] * ctx.height
    lancer = Lancer(200, first, first)
    run_until(lancer, ctx, lambda: lancer.state == "attack", limit=10.0)
    run_until(lancer, ctx, lambda: lancer.state == "move", limit=10.0)
    assert lancer.charge == 0
    # It never backs away: it eases off, straight down, without turning.
    run(lancer, ctx, 0.5)
    assert lancer.x == 200
    assert lancer.y < first
    assert 0 < lancer._speed < CFG.cruiseSpeed
    run_until(lancer, ctx, lambda: lancer.state == "attack", limit=20.0)
    assert lancer.y == pytest.approx(first - CFG.stepFraction * ctx.height)
    assert len(ctx.lasers) == 2


def test_enm_lancer_07_below_its_last_stop_a_lancer_leaves_through_the_bottom() -> None:
    ctx = FakeContext()
    stop = (CFG.lastStopFraction + CFG.stepFraction / 2) * ctx.height
    lancer = Lancer(200, stop, stop)
    run_until(lancer, ctx, lambda: lancer.state == "attack", limit=10.0)
    run_until(lancer, ctx, lambda: lancer.state == "move", limit=10.0)
    # Its next stop would be under `lastStopFraction`: none, it speeds up out of the screen.
    assert lancer.stop_y is None
    run_until(lancer, ctx, lambda: lancer.y < 0, limit=20.0)
    assert lancer.y < 0
    assert lancer._speed == CFG.exitSpeed
    assert len(ctx.lasers) == 1


def test_enm_lancer_06_the_laser_beam_follows_the_lancers_nose_and_heading() -> None:
    lancer = Lancer(200, 300, 300)
    beam = LancerBeam(lancer, CFG.muzzle)
    assert beam.heading == lancer.heading
    assert beam.gone is False
    assert beam.health == lancer.health
    assert beam.emitter is not None
