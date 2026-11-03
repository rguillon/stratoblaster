# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/phantom.py`."""

import math
from typing import Any

import pytest
from helpers.enemy_steps import area, run, run_until
from helpers.fakes import FakeContext

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.phantom import Phantom
from game.sim.enemy_kinds import ENEMY_KINDS

PHANTOM = next(kind for kind in ENEMY_KINDS if kind.id == "phantom")
SOLID = VETERAN_CONFIG.phantom.solidOpacity


def test_enm_phantom_12_a_faded_phantom_is_cloaked_and_shots_pass_through_it() -> None:
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    phantom.opacity = 0.0
    assert phantom.cloaked is True
    assert phantom._hit_targets() == []


def test_enm_phantom_12_a_phantom_solid_enough_can_be_hit() -> None:
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    phantom.opacity = SOLID + 0.01
    assert phantom.cloaked is False
    assert phantom._hit_targets() != []


def test_enm_phantom_09_a_phantom_runs_its_fade_cycle_with_its_opacity_in_range() -> None:
    ctx = FakeContext()
    (phantom,) = PHANTOM.spawn(area(width=400, height=600))
    run(phantom, ctx, 12.0)
    assert 0 <= phantom.opacity <= 1


def _draws(values: list[float]) -> Any:
    """Return random draws that give `values` in turn."""
    left = list(values)

    def draw() -> float:
        return left.pop(0)

    return draw


def test_enm_phantom_09_a_phantom_reappears_away_from_where_it_faded() -> None:
    ctx = FakeContext()
    # The middle of its places (draws of 0.5) is where it fades out; the next try is far enough.
    phantom = Phantom(200, 426, 426)
    run_until(phantom, ctx, lambda: phantom.state == "hidden", limit=5.0)
    ctx.random = _draws([0.5, 0.5, 0.0, 0.0])
    run_until(phantom, ctx, lambda: phantom.state == "fadeIn", limit=5.0)
    cfg = VETERAN_CONFIG.phantom
    assert (phantom.x, phantom.y) == pytest.approx((cfg.placeX[0] * 400, cfg.placeY[0] * 600))


def _until(phantom: Phantom, ctx: Any, state: str, limit: float = 10.0) -> None:
    run_until(phantom, ctx, lambda: phantom.state == state, limit=limit)
    assert phantom.state == state


def test_enm_phantom_09_it_cloaks_twice_and_then_aims_and_dives() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    states: list[str] = []
    run_until(phantom, ctx, lambda: states.append(phantom.state) or phantom.state == "dive", 30.0)
    assert states.count("hidden") > 0
    assert phantom.jumps == VETERAN_CONFIG.phantom.jumps == 2
    seen = [s for i, s in enumerate(states) if i == 0 or states[i - 1] != s]
    assert seen == [
        *["enter", "hold", "fadeOut", "hidden", "fadeIn"],
        *["hold", "fadeOut", "hidden", "fadeIn", "aim", "dive"],
    ]


def test_enm_phantom_10_it_fires_its_spread_once_after_the_first_jump_only() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "hold")
    assert ctx.bullets == []
    _until(phantom, ctx, "fadeIn")
    _until(phantom, ctx, "hold")
    assert len(ctx.bullets) == VETERAN_CONFIG.phantom.spreadCount
    assert phantom.jumps == 1
    _until(phantom, ctx, "dive", limit=30.0)
    assert len(ctx.bullets) == VETERAN_CONFIG.phantom.spreadCount


def test_enm_phantom_11_it_turns_its_nose_to_the_player_then_dives_at_where_he_was() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "aim", limit=30.0)
    ctx.player_x = phantom.x + 100
    ctx.player_y = phantom.y - 100
    expected = math.atan2(100, -100)
    run_until(phantom, ctx, lambda: phantom.state == "dive", limit=2.0)
    assert phantom.dive_heading == pytest.approx(expected)
    assert phantom.heading == pytest.approx(expected)
    # The player moves on: the dive keeps its line, accelerating from rest.
    ctx.player_x = 0
    start = (phantom.x, phantom.y)
    run(phantom, ctx, 0.1)
    first = math.hypot(phantom.x - start[0], phantom.y - start[1])
    run(phantom, ctx, 0.1)
    second = math.hypot(phantom.x - start[0], phantom.y - start[1]) - first
    assert 0 < first < second
    assert phantom.heading == pytest.approx(expected)


def test_enm_phantom_11_the_dive_has_a_top_speed_and_leaves_the_screen_at_the_bottom() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "dive", limit=30.0)
    ctx.player_x = phantom.x
    run_until(phantom, ctx, lambda: phantom.y < -50, limit=5.0)
    assert phantom.y < -50
    assert phantom._speed == VETERAN_CONFIG.phantom.diveMaxSpeed
    assert phantom.opacity == 1


def test_enm_phantom_08_a_phantom_launched_below_its_stop_height_rises_to_it() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 300, 450)
    _until(phantom, ctx, "hold", limit=10.0)
    assert phantom.y == 450


def test_enm_phantom_04_its_charge_follows_the_fade_in_and_the_aim() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "fadeIn")
    run(phantom, ctx, 0.2)
    assert phantom.charge == pytest.approx(phantom.opacity)
    _until(phantom, ctx, "hold")
    assert phantom.charge == 0
    _until(phantom, ctx, "aim", limit=30.0)
    run(phantom, ctx, 0.25)
    assert 0 < phantom.charge < 1
    _until(phantom, ctx, "dive")
    assert phantom.charge == 0
