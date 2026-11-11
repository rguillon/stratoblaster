# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/phantom.py`."""

import itertools
import math

import pytest
from helpers.enemy_steps import run, run_until
from helpers.fakes import FakeContext

from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.phantom import Phantom

CFG = VETERAN_CONFIG.phantom


def _until(phantom: Phantom, ctx: FakeContext, state: str, limit: float = 10.0) -> None:
    run_until(phantom, ctx, lambda: phantom.state == state, limit=limit)
    assert phantom.state == state


def _states(phantom: Phantom, ctx: FakeContext, until: str, limit: float = 30.0) -> list[str]:
    """Return the states `phantom` goes through, each once in a row, until it is in `until`."""
    states: list[str] = [phantom.state]

    def done() -> bool:
        if states[-1] != phantom.state:
            states.append(phantom.state)
        return phantom.state == until

    run_until(phantom, ctx, done, limit=limit)
    return states


def test_enm_phantom_08_a_phantom_launched_below_its_stop_height_rises_to_it() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 300, 450)
    _until(phantom, ctx, "hold", limit=10.0)
    assert phantom.y == 450


def test_enm_phantom_09_it_fires_from_each_of_its_places_then_locks_on_and_dives() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    states = _states(phantom, ctx, "dive")
    assert CFG.stops == 2
    assert states == [*["fly", "aim", "hold"] * CFG.stops, "lock", "dive"]
    assert phantom.stops_left == 0


def test_d_313_a_phantom_flies_on_to_another_place_down_to_below_the_middle() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "hold")
    first = (phantom.x, phantom.y)
    _until(phantom, ctx, "fly")
    target = (phantom.target_x, phantom.target_y)
    # Somewhere else, far enough from where it fired.
    assert CFG.placeX[0] * ctx.width <= target[0] <= CFG.placeX[1] * ctx.width
    assert CFG.placeY[0] * ctx.height <= target[1] <= CFG.placeY[1] * ctx.height
    assert CFG.placeY[0] < 0.5 < CFG.placeY[1]
    assert math.hypot(target[0] - first[0], target[1] - first[1]) >= CFG.moveDistance
    _until(phantom, ctx, "aim")
    assert (phantom.x, phantom.y) == target


def test_enm_phantom_09_between_places_it_speeds_up_then_brakes_into_the_next() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "hold")
    _until(phantom, ctx, "fly")
    speeds: list[float] = []
    run_until(
        phantom, ctx, lambda: speeds.append(phantom._speed) or phantom.state != "fly", limit=10.0
    )
    top = max(speeds)
    peak = speeds.index(top)
    assert 0 < peak < len(speeds) - 2
    # It speeds up from rest, up to its cruise speed at most...
    assert speeds[0] < top <= CFG.cruiseSpeed
    assert all(a <= b for a, b in itertools.pairwise(speeds[: peak + 1]))
    # ...then brakes into its place, where it stops.
    assert speeds[-2] < top / 2
    assert phantom._speed == 0


def test_enm_phantom_10_it_turns_its_nose_to_the_player_then_fires_a_spread_at_each_place() -> None:
    ctx = FakeContext()
    ctx.player_x = 320
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "aim")
    assert ctx.bullets == []
    run(phantom, ctx, CFG.aimTime / 2)
    assert phantom.state == "aim"
    assert ctx.bullets == []
    _until(phantom, ctx, "hold")
    want = math.atan2(ctx.player_x - phantom.x, ctx.player_y - phantom.y)
    # Its nose has come round to the player in `aimTime`.
    assert abs(math.remainder(phantom.heading - want, math.tau)) < math.radians(6)
    assert CFG.spreadCount == 5
    assert CFG.spreadSpacing == 12
    assert len(ctx.bullets) == CFG.spreadCount
    # 5 bullets 12 degrees apart, centred on the player.
    headings = sorted(heading for _x, _y, heading, _spec in ctx.bullets)
    for a, b in itertools.pairwise(headings):
        assert b - a == pytest.approx(math.radians(CFG.spreadSpacing))
    assert abs(math.remainder(headings[2] - want, math.tau)) < math.radians(6)
    assert all(spec == CFG.bullet for *_rest, spec in ctx.bullets)
    _until(phantom, ctx, "lock", limit=20.0)
    assert len(ctx.bullets) == CFG.spreadCount * CFG.stops
    _until(phantom, ctx, "dive")
    run(phantom, ctx, 1.0)
    assert len(ctx.bullets) == CFG.spreadCount * CFG.stops


def test_enm_phantom_10_its_holds_get_shorter_with_the_fire_rate() -> None:
    slow = FakeContext()
    fast = FakeContext()
    fast.fire_rate = 2.0
    held = []
    for ctx in (slow, fast):
        phantom = Phantom(200, 426, 426)
        _until(phantom, ctx, "hold")
        held.append(run_until(phantom, ctx, lambda p=phantom: p.state != "hold", limit=5.0))
    assert held[0] == pytest.approx(CFG.hold, abs=0.05)
    assert held[1] == pytest.approx(CFG.hold / 2, abs=0.05)


def test_enm_phantom_11_it_turns_its_nose_to_the_player_then_dives_at_where_he_was() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "lock", limit=30.0)
    ctx.player_x = phantom.x + 100
    ctx.player_y = phantom.y - 100
    expected = math.atan2(100, -100)
    locked = run_until(phantom, ctx, lambda: phantom.state == "dive", limit=2.0)
    assert locked == pytest.approx(CFG.pause, abs=0.05)
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
    _until(phantom, ctx, "lock", limit=30.0)
    ctx.player_x = phantom.x
    _until(phantom, ctx, "dive")
    run_until(phantom, ctx, lambda: phantom.y < -50, limit=5.0)
    assert phantom.y < -50
    assert phantom._speed == CFG.diveMaxSpeed


def test_enm_phantom_04_its_charge_follows_the_aim_and_the_lock() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    assert phantom.charge == 0
    _until(phantom, ctx, "aim")
    run(phantom, ctx, CFG.aimTime / 2)
    assert phantom.charge == pytest.approx(0.5, abs=0.05)
    _until(phantom, ctx, "hold")
    assert phantom.charge == 0
    _until(phantom, ctx, "lock", limit=30.0)
    run(phantom, ctx, CFG.pause / 2)
    assert phantom.charge == pytest.approx(0.5, abs=0.05)
    _until(phantom, ctx, "dive")
    assert phantom.charge == 0


def test_enm_phantom_12_it_no_longer_cloaks_shots_can_hit_it_all_along() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    hittable: list[bool] = []
    run_until(
        phantom,
        ctx,
        lambda: hittable.append(phantom._hit_targets() != []) or phantom.state == "dive",
        limit=30.0,
    )
    assert phantom.state == "dive"
    assert all(hittable)


def test_enm_phantom_08_a_phantom_at_rest_on_its_place_settles_without_turning() -> None:
    """A step of no time, at rest on its place: it settles there, its nose left as it was."""
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    phantom._speed = 0.0
    phantom.heading = 1.0
    phantom.update(ctx, 0.0)
    assert phantom.state == "aim"
    assert phantom.heading == 1.0
    assert (phantom.x, phantom.y) == (200, 426)


def test_enm_phantom_09_a_place_too_near_is_drawn_again() -> None:
    ctx = FakeContext()
    phantom = Phantom(200, 426, 426)
    _until(phantom, ctx, "hold")
    here = (phantom.x, phantom.y)
    far = (here[0] + CFG.moveDistance + 10, here[1])
    picks = iter([here, here, far])
    phantom._pick_place = lambda _ctx: next(picks)  # type: ignore[method-assign]
    _until(phantom, ctx, "fly")
    assert (phantom.target_x, phantom.target_y) == far
