# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/carrier_guns.py` (WPN-02: the carriers' gun turrets)."""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.enemy_steps import STEP, run, run_until
from helpers.fakes import FakeContext

from core.entities.enemy import Enemy, EnemyStats
from game.sim.enemies.carrier_guns import AIMED, CarrierGuns
from game.sim.enemies.enemy_helpers import DOWN

BULLET = {"speed": 190, "radius": 4, "style": "green"}


def guns_config(**changes: Any) -> Any:
    """Return a `turrets` config: one turret on the centre, turning at 90 degrees a second."""
    values: dict[str, Any] = {
        "pivots": [[0, 0]],
        "barrel": 10,
        "height": 1,
        "turnDeg": 90,
        "fireInterval": 1,
        "firstShot": 0.1,
        "bullet": BULLET,
    }
    values.update(changes)
    return SimpleNamespace(**values)


class GunCarrier(Enemy):
    """A still carrier facing down the screen, with nothing but its gun turrets."""

    def __init__(self, x: float, y: float, config: Any) -> None:
        super().__init__(x, y, EnemyStats("carrier", 20, 100, 10))
        self.heading = DOWN
        self.guns = CarrierGuns(config)
        self.turrets = self.guns.turrets
        self.barrels = self.guns.barrels

    def update(self, ctx: Any, dt: float) -> None:
        self.guns.update(self, ctx, dt)


def _player_to_the_right(ctx: FakeContext, carrier: GunCarrier) -> None:
    """Put the player square to the right of `carrier`, a quarter turn from its turrets' rest."""
    ctx.player_x = carrier.x + 1000
    ctx.player_y = carrier.y


def test_wpn_02_a_turret_rests_pointing_down_with_its_barrel_ahead_of_its_pivot() -> None:
    carrier = GunCarrier(200, 400, guns_config(pivots=[[-20, 5], [20, 5]]))
    assert [turret.aim for turret in carrier.turrets] == [0, 0]
    assert [(t.spec.x, t.spec.y, t.spec.turn_rate_deg) for t in carrier.turrets] == [
        (-20, 5, 90),
        (20, 5, 90),
    ]
    assert [barrel.muzzle for barrel in carrier.barrels] == [(-20, -5, 1), (20, -5, 1)]


def test_wpn_02_a_turret_turns_towards_the_player_at_its_turn_rate() -> None:
    ctx = FakeContext()
    carrier = GunCarrier(200, 400, guns_config())
    _player_to_the_right(ctx, carrier)
    run(carrier, ctx, 0.5)
    # A quarter turn to make: 45 degrees done after half a second.
    turret = carrier.turrets[0]
    assert abs(turret.aim) == pytest.approx(math.radians(45), abs=math.radians(1))
    assert math.sin(carrier.heading + turret.aim) > 0
    run(carrier, ctx, 1.0)
    assert carrier.heading + turret.aim == pytest.approx(math.pi / 2)


def test_wpn_02_a_turret_fires_only_once_it_points_within_6_degrees_of_the_player() -> None:
    ctx = FakeContext()
    carrier = GunCarrier(200, 400, guns_config())
    _player_to_the_right(ctx, carrier)
    assert math.degrees(AIMED) == pytest.approx(6)
    # Its first shot is due at 0.1 s, but it takes (90 - 6) / 90 s to come round.
    waited = run_until(carrier, ctx, lambda: ctx.bullets != [], limit=3.0)
    assert waited == pytest.approx((90 - 6) / 90, abs=2 * STEP)
    _x, _y, heading, spec = ctx.bullets[0]
    assert abs(math.remainder(heading - math.pi / 2, math.tau)) <= AIMED
    assert spec == BULLET


def test_wpn_02_a_turret_slow_to_come_round_owes_one_shot_at_most() -> None:
    ctx = FakeContext()
    carrier = GunCarrier(200, 400, guns_config(fireInterval=0.2))
    _player_to_the_right(ctx, carrier)
    # Several shots came due while it turned: it fires one, not a burst...
    run_until(carrier, ctx, lambda: ctx.bullets != [], limit=3.0)
    run(carrier, ctx, 0.1)
    assert len(ctx.bullets) == 1
    # ...then one each `fireInterval`.
    run(carrier, ctx, 1.0)
    assert len(ctx.bullets) == 1 + 5


def test_wpn_02_its_shots_come_faster_with_the_fire_rate() -> None:
    slow = FakeContext()
    fast = FakeContext()
    fast.fire_rate = 2.0
    for ctx in (slow, fast):
        run(GunCarrier(200, 400, guns_config(firstShot=1)), ctx, 3.95)
    # Straight below it: aimed from the start, it fires on its cadence.
    assert len(slow.bullets) == 3
    assert len(fast.bullets) == 7


def test_wpn_01_a_turret_fires_from_its_barrels_tip_along_it_and_the_barrel_kicks() -> None:
    ctx = FakeContext()
    carrier = GunCarrier(200, 400, guns_config(pivots=[[-20, 5]], barrel=10))
    _player_to_the_right(ctx, carrier)
    run_until(carrier, ctx, lambda: ctx.bullets != [], limit=3.0)
    x, y, heading, _spec = ctx.bullets[0]
    # The tip is the barrel's length from the pivot, the way the turret points.
    pivot = (200 - 20, 400 + 5)
    assert math.hypot(x - pivot[0], y - pivot[1]) == pytest.approx(10)
    assert math.atan2(x - pivot[0], y - pivot[1]) == pytest.approx(heading)
    barrel = carrier.barrels[0]
    assert barrel.fired_at == carrier.age
    assert barrel.recoil_at(carrier.age) > 0


def test_wpn_02_each_turret_turns_on_its_own_towards_the_player() -> None:
    ctx = FakeContext()
    carrier = GunCarrier(200, 400, guns_config(pivots=[[-100, 0], [100, 0]], turnDeg=360))
    ctx.player_x = 200
    ctx.player_y = 300
    run(carrier, ctx, 1.0)
    left, right = (carrier.heading + turret.aim for turret in carrier.turrets)
    assert math.remainder(left - math.atan2(100, -100), math.tau) == pytest.approx(0)
    assert math.remainder(right - math.atan2(-100, -100), math.tau) == pytest.approx(0)
    # Each fired its shot from its own barrel, along it, towards the player.
    assert len(ctx.bullets) == 2
    for x, y, heading, _spec in ctx.bullets:
        pivot = (100, 400) if x < 200 else (300, 400)
        assert math.hypot(x - pivot[0], y - pivot[1]) == pytest.approx(10)
        assert math.remainder(math.atan2(x - pivot[0], y - pivot[1]) - heading, math.tau) == (
            pytest.approx(0)
        )
        want = math.atan2(ctx.player_x - pivot[0], ctx.player_y - pivot[1])
        assert abs(math.remainder(heading - want, math.tau)) <= AIMED
