# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/prism.py`."""

import math

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_prism import PRISM_CONFIG
from game.config.enemy_tiers import ENEMY_TIERS, tier_of
from game.sim.enemies.enemy_helpers import DEG, DOWN
from game.sim.enemies.prism import Prism, PrismBeam
from game.sim.enemy_kinds import ENEMY_KINDS

CFG = PRISM_CONFIG
KIND = next(kind for kind in ENEMY_KINDS if kind.id == "prism")
WARNING = CFG.laser.warningSeconds
FIRING = CFG.laser.firingSeconds


def _stopped(ctx: FakeContext) -> Prism:
    prism = Prism(200, 300, 300)
    run_until(prism, ctx, lambda: prism.state == "attack", limit=10.0)
    return prism


def test_enm_prism_05_the_kind_spawns_one_prism_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert len(enemies) == 1
    assert isinstance(enemies[0], Prism)
    assert enemies[0].y > 600
    assert enemies[0].stop_y == pytest.approx(CFG.stopFraction * 600)


def test_enm_prism_05_a_prism_comes_in_and_stops_in_the_upper_third() -> None:
    ctx = FakeContext()
    prism = Prism(200, 500, 470)
    run_until(prism, ctx, lambda: prism.state != "enter", limit=10.0)
    assert prism.y == pytest.approx(470)
    assert prism.state == "attack"
    assert CFG.stopFraction * 600 > 600 * 2 / 3


def test_enm_prism_06_it_shows_two_warning_lines_then_fires_two_sweeping_lasers() -> None:
    ctx = FakeContext()
    _stopped(ctx)
    assert len(ctx.lasers) == 2
    for owner, spec in ctx.lasers:
        assert isinstance(owner, PrismBeam)
        assert spec.warning_seconds == WARNING
        assert spec.firing_seconds == FIRING
        assert spec.width == CFG.laser.width
        assert spec.sweeps is True


def test_enm_prism_04_its_emitters_charge_during_the_warning_and_it_holds_still() -> None:
    ctx = FakeContext()
    prism = _stopped(ctx)
    run(prism, ctx, WARNING / 2)
    assert prism.y == pytest.approx(300)
    assert prism.charge == pytest.approx(0.5, abs=0.02)


def test_enm_prism_07_the_beams_start_outward_apart_and_close_into_a_cross() -> None:
    ctx = FakeContext()
    prism = _stopped(ctx)
    left = ctx.lasers[0][0]
    right = ctx.lasers[1][0]
    # The warning lines point outward: left of down for the left emitter, right for the right one.
    assert math.sin(left.heading) < 0
    assert math.sin(right.heading) > 0
    run(prism, ctx, WARNING + FIRING / 2)
    assert prism.sweep == pytest.approx(
        (CFG.bursts[0].start + CFG.bursts[0].end) / 2 * DEG, abs=0.02
    )
    run(prism, ctx, FIRING / 2 - 0.05)
    # At the end of the burst they point inward, past each other: the beams cross.
    assert math.sin(left.heading) > 0
    assert math.sin(right.heading) < 0


def test_enm_prism_07_the_beams_cross_below_the_prism_and_the_crossing_slides_up_to_it() -> None:
    ctx = FakeContext()
    prism = _stopped(ctx)
    left = ctx.lasers[0][0]
    right = ctx.lasers[1][0]

    def crossing() -> float:
        # Where the two beams meet below the emitters (heading from +Y, DOWN = pi).
        a = left.emitter
        b = right.emitter
        angle = abs(left.heading - DOWN)
        return float((b.x - a.x) / 2 / math.tan(angle))

    run(prism, ctx, WARNING + FIRING * 0.8)
    first = crossing()
    run(prism, ctx, FIRING * 0.15)
    # Both beams point inward at both sample times; the crossing comes closer to the Prism.
    assert math.sin(left.heading) > 0
    assert crossing() < first


def test_enm_prism_08_a_second_burst_opens_the_beams_again_then_it_leaves_upward() -> None:
    ctx = FakeContext()
    prism = _stopped(ctx)
    run_until(prism, ctx, lambda: prism.state == "gap", limit=10.0)
    assert prism.charge == 0
    assert prism.burst == 1
    assert prism.sweep == pytest.approx(CFG.bursts[0].end * DEG)
    assert len(ctx.lasers) == 2
    # The gap is still: no new laser until it is over.
    run(prism, ctx, CFG.gapSeconds / 2)
    assert len(ctx.lasers) == 2
    run_until(prism, ctx, lambda: len(ctx.lasers) == 4, limit=5.0)
    assert prism.state == "attack"
    assert prism.sweep == pytest.approx(CFG.bursts[1].start * DEG)
    run_until(prism, ctx, lambda: prism.state == "exit", limit=10.0)
    assert prism.charge == 0
    assert prism.sweep == pytest.approx(CFG.bursts[1].end * DEG)
    y = prism.y
    run(prism, ctx, 0.5)
    assert prism.y == pytest.approx(y + CFG.exitSpeed * 0.5, rel=1e-2)


def test_enm_prism_07_the_beam_follows_the_prisms_wing_emitters_and_heading() -> None:
    prism = Prism(200, 300, 300)
    left = PrismBeam(prism, CFG.emitters[0])
    right = PrismBeam(prism, CFG.emitters[1])
    assert left.emitter.x < prism.x < right.emitter.x
    assert left.gone is False
    assert left.health == prism.health
    # A turn outward points the left beam left of down and the right one right of it.
    prism.sweep = 30 * DEG
    assert left.heading == pytest.approx(DOWN + 30 * DEG)
    assert right.heading == pytest.approx(DOWN - 30 * DEG)
    # Inward, they swap.
    prism.sweep = -30 * DEG
    assert left.heading == pytest.approx(DOWN - 30 * DEG)
    assert right.heading == pytest.approx(DOWN + 30 * DEG)


def test_enm_prism_12_prism_has_150_health_and_scores_380_points() -> None:
    prism = Prism(200, 300, 300)
    assert prism.health == 150
    assert prism.points == 380
    assert CFG.size == 1.5


def test_enm_prism_09_the_emitters_are_fixed_on_the_hull_and_cannot_be_shot_off() -> None:
    ctx = FakeContext()
    prism = _stopped(ctx)
    beam = ctx.lasers[0][0]
    at = (beam.emitter.x, beam.emitter.y)
    run(prism, ctx, WARNING + FIRING / 2)
    assert (beam.emitter.x, beam.emitter.y) == pytest.approx(at)
    # The only thing to hit is the Prism itself.
    assert prism.hit_targets == [prism]


def test_enm_prism_10_prism_is_a_tier_3_kind_in_its_tiers_neon() -> None:
    assert tier_of("prism") == 3
    assert ENEMY_TIERS["3"].kinds.laser == "prism"
    assert ENEMY_LOOK.neon.prism == ENEMY_TIERS["3"].neon


def test_enm_prism_11_the_lasers_timing_does_not_follow_the_levels_fire_rate() -> None:
    ctx = FakeContext()
    ctx.fire_rate = 2.0
    _stopped(ctx)
    for _owner, spec in ctx.lasers:
        assert spec.warning_seconds == WARNING
        assert spec.firing_seconds == FIRING
