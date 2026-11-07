# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/prism.py`."""

import itertools
import math

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.config.enemy_look import ENEMY_LOOK
from game.config.enemy_prism import PRISM_CONFIG
from game.config.enemy_tiers import ENEMY_TIERS, tier_of
from game.sim.enemies.enemy_helpers import DOWN
from game.sim.enemies.prism import Prism, PrismBeam
from game.sim.enemy_kinds import ENEMY_KINDS

CFG = PRISM_CONFIG
KIND = next(kind for kind in ENEMY_KINDS if kind.id == "prism")
WARNING = CFG.laser.warningSeconds
FIRING = CFG.laser.firingSeconds


def _stopped(ctx: FakeContext) -> Prism:
    prism = Prism(200, 600, 300)
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
    prism = Prism(200, 700, 470)
    run_until(prism, ctx, lambda: prism.state != "enter", limit=10.0)
    assert prism.y == pytest.approx(470)
    assert prism.state == "attack"
    assert CFG.stopFraction * 600 > 600 * 2 / 3


def test_enm_prism_06_it_shows_two_warning_lines_then_fires_two_straight_lasers() -> None:
    ctx = FakeContext()
    _stopped(ctx)
    assert len(ctx.lasers) == 2
    for owner, spec in ctx.lasers:
        assert isinstance(owner, PrismBeam)
        assert spec.warning_seconds == WARNING
        assert spec.firing_seconds == FIRING
        assert spec.width == CFG.laser.width
        assert spec.sweeps is False


def test_enm_prism_04_its_emitters_charge_during_the_warning_and_it_holds_still() -> None:
    ctx = FakeContext()
    prism = _stopped(ctx)
    run(prism, ctx, WARNING / 2)
    assert prism.y == pytest.approx(300)
    assert prism.charge == pytest.approx(0.5, abs=0.02)


def test_enm_prism_05_it_comes_in_fast_and_slows_down_to_a_stop() -> None:
    ctx = FakeContext()
    prism = Prism(200, 900, 470)
    speeds = []
    while prism.state == "enter":
        before = prism.y
        run(prism, ctx, 0.05)
        speeds.append((before - prism.y) / 0.05)
    assert max(speeds) == pytest.approx(CFG.entrySpeed, rel=0.02)
    # It is slower and slower on the way in, never speeding up again.
    peak = speeds.index(max(speeds))
    tail = speeds[peak:]
    assert all(b <= a + 1e-6 for a, b in itertools.pairwise(tail))
    assert tail[-2] < CFG.entrySpeed / 4


def test_enm_prism_07_it_turns_to_the_player_while_slowing_down_and_fires_only_when_stopped() -> (
    None
):
    ctx = FakeContext()
    ctx.player_x = 400
    ctx.player_y = 0
    prism = Prism(200, 900, 470)
    turned_while_moving = False
    while prism.state == "enter":
        assert ctx.lasers == []
        run(prism, ctx, 0.05)
        if prism.state == "enter" and prism.y > prism.stop_y and prism.heading != DOWN:
            turned_while_moving = True
    assert turned_while_moving
    # Stopped: it fires at once, aimed at the player.
    assert prism.state == "attack"
    assert len(ctx.lasers) == 2
    expected = math.atan2(400 - 200, 0 - 470)
    assert prism.heading == pytest.approx(expected, abs=0.1)


def test_enm_prism_07_both_beams_point_straight_ahead_and_it_stops_turning_once_firing() -> None:
    ctx = FakeContext()
    ctx.player_x = 400
    ctx.player_y = 0
    prism = Prism(200, 300, 300)
    run_until(prism, ctx, lambda: prism.state == "attack", limit=10.0)
    locked = prism.heading
    left = ctx.lasers[0][0]
    right = ctx.lasers[1][0]
    assert left.heading == pytest.approx(locked)
    assert right.heading == pytest.approx(locked)
    # The player moves to the other side: the nose does not follow while it shoots.
    ctx.player_x = 0
    run(prism, ctx, WARNING + FIRING - 0.1)
    assert prism.heading == pytest.approx(locked)
    assert left.heading == pytest.approx(locked)


def test_enm_prism_08_it_aims_again_for_a_second_burst_then_leaves_upward() -> None:
    ctx = FakeContext()
    ctx.player_x = 400
    ctx.player_y = 0
    prism = Prism(200, 300, 300)
    run_until(prism, ctx, lambda: prism.state == "attack", limit=10.0)
    ctx.player_x = 0
    run_until(prism, ctx, lambda: prism.state == "aim", limit=10.0)
    assert prism.charge == 0
    assert prism.burst == 1
    assert len(ctx.lasers) == 2
    run_until(prism, ctx, lambda: prism.state == "attack", limit=5.0)
    assert len(ctx.lasers) == 4
    assert math.sin(prism.heading) < 0.5
    run_until(prism, ctx, lambda: prism.state == "exit", limit=10.0)
    assert prism.charge == 0
    y = prism.y
    run(prism, ctx, 0.5)
    assert prism.y == pytest.approx(y + CFG.exitSpeed * 0.5, rel=1e-2)
    # Its nose turns round to the way it flies.
    run(prism, ctx, 2.0)
    assert prism.heading == pytest.approx(0)


def test_enm_prism_07_the_beam_follows_the_prisms_wing_emitters_and_heading() -> None:
    prism = Prism(200, 300, 300)
    left = PrismBeam(prism, CFG.emitters[0])
    right = PrismBeam(prism, CFG.emitters[1])
    assert left.emitter.x < prism.x < right.emitter.x
    assert left.gone is False
    assert left.health == prism.health
    prism.heading = 0.4
    assert left.heading == pytest.approx(0.4)
    assert right.heading == pytest.approx(0.4)


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
