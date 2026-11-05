# Copyright (c) 2026 Renaud Guillon
"""WPN-01, WPN-04: the bullets of the converted enemies leave their barrels, along them."""

import math
from typing import Any

import pytest
from helpers.enemy_steps import STEP, run
from helpers.fakes import FakeContext

from game.sim.enemies.hive import Hive
from game.sim.enemies.juggernaut import Juggernaut
from game.sim.enemies.phantom import Phantom
from game.sim.enemies.scout import Scout
from game.sim.enemies.spinner import Spinner
from game.sim.enemies.wasp import Wasp


def _first_volley(enemy: Any, ctx: FakeContext, limit: float = 30) -> None:
    for _ in range(int(limit / STEP)):
        run(enemy, ctx, STEP)
        if ctx.bullets:
            return
    pytest.fail("no bullet fired")


def _tips(enemy: Any) -> list[tuple[float, float, float]]:
    """Each barrel's tip and heading now, with the enemy's turret if its guns are on it."""
    on_turret = enemy.turret is not None
    tips = []
    for barrel in enemy.barrels:
        if barrel.angle is None and not on_turret:
            continue
        tip = enemy.place(barrel.muzzle, on_turret)
        own = enemy.heading + (enemy.turret.aim if on_turret else barrel.angle)
        tips.append((tip.x, tip.y, own))
    return tips


@pytest.mark.parametrize(
    "build",
    [
        lambda: Scout(200, 560),
        lambda: Wasp(200, 520, 400),
        lambda: Phantom(200, 520, 400),
        lambda: Juggernaut(200, 700, 500),
        lambda: Spinner(200, 700, 500),
        lambda: Hive(200, 620),
    ],
    ids=["scout", "wasp", "phantom", "juggernaut", "spinner", "hive"],
)
def test_wpn_01_each_bullet_starts_at_a_barrel_tip_and_flies_along_it(build: Any) -> None:
    enemy = build()
    ctx = FakeContext()
    _first_volley(enemy, ctx)
    assert enemy.barrels
    tips = _tips(enemy)
    for x, y, heading, _spec in ctx.bullets:
        assert any(
            math.hypot(tx - x, ty - y) < 0.01 and abs(math.remainder(th - heading, math.tau)) < 1e-4
            for tx, ty, th in tips
        ), (x, y, heading)


def test_wpn_03_a_barrel_that_fired_recoils() -> None:
    spinner = Spinner(200, 700, 500)
    ctx = FakeContext()
    _first_volley(spinner, ctx)
    assert any(b.recoil_at(spinner.age) > 0 for b in spinner.barrels)


def test_wpn_02_a_scouts_gun_turns_to_the_player_before_it_fires() -> None:
    ctx = FakeContext()
    scout = Scout(200, 560)
    _first_volley(scout, ctx)
    # The bullet flies where the barrel points, and that is towards the player (within the
    # tolerance).
    _, _, heading, _ = ctx.bullets[0]
    want = math.atan2(ctx.player_x - scout.x, ctx.player_y - scout.y)
    assert abs(math.remainder(heading - want, math.tau)) < math.radians(8)
