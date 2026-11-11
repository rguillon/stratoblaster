# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/sweeper.py`."""

import itertools
import math

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.config.enemy_sweeper import SWEEPER_CONFIG
from game.sim.enemies.sweeper import Sweeper, SweeperBeam
from game.sim.enemy_kinds import ENEMY_KINDS

CFG = SWEEPER_CONFIG
KIND = next(kind for kind in ENEMY_KINDS if kind.id == "sweeper")
ARC = math.radians(CFG.arcDeg)


def test_enm_sweeper_05_the_kind_spawns_a_live_sweeper_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert len(enemies) == 1
    sweeper = enemies[0]
    assert isinstance(sweeper, Sweeper)
    assert sweeper.health > 0
    assert sweeper.y > 600
    assert CFG.stopRange[0] * 600 <= sweeper.stop_y <= CFG.stopRange[1] * 600


def test_enm_sweeper_05_it_stops_in_the_upper_part_and_shows_its_warning() -> None:
    ctx = FakeContext()
    sweeper = Sweeper(200, 700, 470)
    run_until(sweeper, ctx, lambda: sweeper.state == "attack", limit=10.0)
    assert sweeper.y == pytest.approx(470)
    assert len(ctx.lasers) == 1
    owner, spec = ctx.lasers[0]
    assert isinstance(owner, SweeperBeam)
    assert spec.warning_seconds == CFG.laser.warningSeconds
    assert spec.firing_seconds == CFG.laser.firingSeconds
    assert spec.width == CFG.laser.width
    run(sweeper, ctx, 1.0)
    assert sweeper.y == pytest.approx(470)


def test_enm_sweeper_06_the_warning_line_holds_the_first_heading_while_it_charges() -> None:
    ctx = FakeContext()
    sweeper = Sweeper(200, 470, 470)
    run(sweeper, ctx, 0.01)
    first = sweeper.heading
    run(sweeper, ctx, CFG.laser.warningSeconds / 2)
    assert sweeper.heading == pytest.approx(first, abs=1e-3)
    assert sweeper.charge == pytest.approx(0.5, abs=0.03)
    run(sweeper, ctx, CFG.laser.warningSeconds / 2)
    assert sweeper.charge == 1


def test_enm_sweeper_07_its_beam_sweeps_across_the_arc_while_it_fires() -> None:
    ctx = FakeContext()
    sweeper = Sweeper(200, 470, 470)
    run(sweeper, ctx, 0.01)
    first = sweeper.heading
    assert ctx.lasers[0][1].sweeps is True
    run(sweeper, ctx, CFG.laser.warningSeconds + CFG.laser.firingSeconds / 2)
    assert abs(sweeper.heading - first) == pytest.approx(ARC / 2, abs=0.05)
    run_until(sweeper, ctx, lambda: sweeper.state == "exit", limit=10.0)
    assert abs(sweeper.heading - first) == pytest.approx(ARC, abs=1e-6)


def test_enm_sweeper_07_it_starts_far_from_the_player_and_sweeps_towards_them() -> None:
    ctx = FakeContext()
    ctx.player_x = 300
    left = Sweeper(100, 470, 470)
    run(left, ctx, 0.01)
    # Player to its right: the beam starts on the left (a heading above straight down).
    assert left.heading > math.pi
    run_until(left, ctx, lambda: left.state == "exit", limit=10.0)
    assert left.heading < math.pi
    ctx.player_x = 50
    right = Sweeper(100, 470, 470)
    run(right, ctx, 0.01)
    assert right.heading < math.pi
    run_until(right, ctx, lambda: right.state == "exit", limit=10.0)
    assert right.heading > math.pi


def test_enm_sweeper_08_it_backs_away_upward_after_its_laser() -> None:
    ctx = FakeContext()
    sweeper = Sweeper(200, 470, 470)
    run_until(sweeper, ctx, lambda: sweeper.state == "exit", limit=10.0)
    assert sweeper.charge == 0
    y = sweeper.y
    run(sweeper, ctx, 0.5)
    assert sweeper.y == pytest.approx(y + CFG.exitSpeed * 0.5, rel=1e-2)
    assert len(ctx.lasers) == 1


def test_enm_sweeper_07_the_beam_follows_the_barrel_and_heading() -> None:
    sweeper = Sweeper(200, 300, 300)
    beam = SweeperBeam(sweeper, CFG.muzzle)
    assert beam.heading == sweeper.heading
    assert beam.gone is False
    assert beam.health == sweeper.health
    assert beam.emitter.x == pytest.approx(200)
    assert beam.emitter.y == pytest.approx(300 + CFG.muzzle[1])
    assert beam.emitter.height == CFG.muzzle[2]
    sweeper.heading = math.pi / 2
    assert beam.heading == math.pi / 2
    sweeper.gone = True
    assert beam.gone is True


def test_d_314_a_sweeper_has_135_health_and_scores_300() -> None:
    sweeper = Sweeper(200, 470, 470)
    assert sweeper.health == 135
    assert sweeper.points == 300
    assert sweeper.model == "sweeper"


def test_enm_sweeper_06_it_turns_to_the_first_edge_smoothly_while_it_brakes() -> None:
    """D-322: no jump of the heading; it reaches the first edge as it stops."""
    ctx = FakeContext()
    ctx.player_x = 300
    sweeper = Sweeper(200, 700, 470)
    headings = [sweeper.heading]
    while sweeper.state == "enter":
        run(sweeper, ctx, 1 / 60)
        headings.append(sweeper.heading)
    # Straight down until it brakes, then a turn of half the arc, in small steps only.
    assert headings[0] == pytest.approx(math.pi)
    steps = [abs(b - a) for a, b in itertools.pairwise(headings)]
    assert max(steps) < math.radians(3)
    # It ends on the left edge (the player to its right), the warning holding it there.
    assert sweeper.heading == pytest.approx(math.pi + ARC / 2)
    held = sweeper.heading
    run(sweeper, ctx, CFG.laser.warningSeconds / 2)
    assert sweeper.heading == pytest.approx(held)
