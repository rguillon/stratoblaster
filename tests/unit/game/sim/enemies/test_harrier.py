# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/harrier.py`."""

import math

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.config.enemy_harrier import HARRIER_CONFIG
from game.sim.enemies.harrier import Harrier
from game.sim.enemy_kinds import ENEMY_KINDS

CFG = HARRIER_CONFIG
KIND = next(kind for kind in ENEMY_KINDS if kind.id == "harrier")


def test_enm_harrier_05_the_kind_spawns_a_live_harrier_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert len(enemies) == 1
    harrier = enemies[0]
    assert isinstance(harrier, Harrier)
    assert harrier.health > 0
    assert harrier.y > 600
    assert CFG.stopRange[0] * 600 <= harrier.stop_y <= CFG.stopRange[1] * 600


def test_enm_harrier_05_it_brakes_and_holds_in_the_upper_third() -> None:
    ctx = FakeContext()
    harrier = Harrier(200, 700, 470)
    run_until(harrier, ctx, lambda: harrier.state == "hold", limit=10.0)
    assert harrier.y == pytest.approx(470)
    assert harrier.state == "hold"
    run(harrier, ctx, 1.0)
    assert harrier.y == pytest.approx(470)


def test_enm_harrier_06_it_strafes_slowly_sideways_and_turns_back_at_the_edges() -> None:
    ctx = FakeContext()
    harrier = Harrier(100, 470, 470)
    harrier.missiles_left = 1000
    run(harrier, ctx, 0.1)
    assert harrier._strafe == 1
    start = harrier.x
    run(harrier, ctx, 1.0)
    assert harrier.x == pytest.approx(start + CFG.strafeSpeed, rel=1e-2)
    # Towards the right edge, then back.
    harrier.x = ctx.width - CFG.strafeMargin
    run(harrier, ctx, 0.1)
    assert harrier._strafe == -1
    harrier.x = CFG.strafeMargin
    run(harrier, ctx, 0.1)
    assert harrier._strafe == 1


def test_enm_harrier_06_it_first_strafes_towards_the_middle() -> None:
    ctx = FakeContext()
    harrier = Harrier(300, 470, 470)
    run(harrier, ctx, 0.1)
    assert harrier._strafe == -1


def test_enm_harrier_07_it_launches_one_homing_missile_every_interval_from_alternate_rails() -> (
    None
):
    ctx = FakeContext()
    harrier = Harrier(200, 470, 470)
    run(harrier, ctx, CFG.firstShot + 0.05)
    assert len(ctx.missiles) == 1
    x0, _y0, heading, spec = ctx.missiles[0]
    assert heading == math.pi
    assert spec.speed == CFG.missile.speed
    run(harrier, ctx, CFG.fireInterval)
    assert len(ctx.missiles) == 2
    # The two rails are either side of its centre.
    assert ctx.missiles[1][0] != pytest.approx(x0, abs=1)


def test_enm_harrier_07_its_missile_is_faster_and_tighter_than_the_rocketeers() -> None:
    rocketeer = ENEMY_CONFIG.rocketeer.missile
    assert CFG.missile.speed > rocketeer.speed
    assert CFG.missile.turnRateDeg > rocketeer.turnRateDeg
    # ENM-18: a missile can be shot down, as the Rocketeer's.
    assert CFG.missile.health > 0
    assert CFG.missile.health == rocketeer.health


def test_enm_harrier_07_its_launches_follow_the_levels_fire_rate() -> None:
    ctx = FakeContext()
    ctx.fire_rate = 2.0
    harrier = Harrier(200, 470, 470)
    run(harrier, ctx, CFG.firstShot / 2 + 0.05)
    assert len(ctx.missiles) == 1


def test_enm_harrier_03_its_rails_charge_towards_the_next_missile() -> None:
    ctx = FakeContext()
    harrier = Harrier(200, 470, 470)
    run(harrier, ctx, CFG.firstShot + 0.05)
    low = harrier.charge
    run(harrier, ctx, CFG.fireInterval / 2)
    assert harrier.charge > low


def test_enm_harrier_08_it_leaves_upward_after_its_last_missile() -> None:
    ctx = FakeContext()
    harrier = Harrier(200, 470, 470)
    run_until(harrier, ctx, lambda: harrier.state == "exit", limit=30.0)
    assert len(ctx.missiles) == CFG.missiles
    assert harrier.missiles_left == 0
    assert harrier.charge == 0
    y = harrier.y
    run(harrier, ctx, 0.5)
    assert harrier.y == pytest.approx(y + CFG.exitSpeed * 0.5, rel=1e-2)
    assert len(ctx.missiles) == CFG.missiles


def test_enm_harrier_07_a_long_frame_never_launches_more_than_its_missiles() -> None:
    ctx = FakeContext()
    harrier = Harrier(200, 470, 470)
    harrier.update(ctx, 0.001)
    harrier.update(ctx, 60.0)
    assert len(ctx.missiles) == CFG.missiles


def test_d_314_a_harrier_has_90_health_and_scores_220() -> None:
    harrier = Harrier(200, 470, 470)
    assert harrier.health == 90
    assert harrier.points == 220
    assert harrier.model == "harrier"
