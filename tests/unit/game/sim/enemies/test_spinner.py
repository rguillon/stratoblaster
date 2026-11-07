# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/spinner.py`."""

import math

from helpers.enemy_steps import area, run
from helpers.fakes import FakeContext

from game.sim.enemies.spinner import Spinner
from game.sim.enemy_kinds import ENEMY_KINDS

KIND = next(kind for kind in ENEMY_KINDS if kind.id == "spinner")


def test_enm_spinner_04_the_kind_spawns_live_enemies_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert enemies
    for enemy in enemies:
        assert enemy.health > 0
        assert math.isfinite(enemy.x)
        assert math.isfinite(enemy.y)


def test_enm_spinner_05_a_spawned_enemy_moves_and_stays_finite_over_a_long_run() -> None:
    ctx = FakeContext()
    enemy = KIND.spawn(area(width=400, height=600))[0]
    start = (enemy.x, enemy.y)
    run(enemy, ctx, 8.0)
    assert math.isfinite(enemy.x)
    assert math.isfinite(enemy.y)
    assert (enemy.x, enemy.y) != start


def test_enm_spinner_05_a_pod_shot_before_the_spinner_has_fired_goes_nowhere() -> None:
    """WPN-01: the pods' bullets go to the world the Spinner fires in; before that, nowhere."""
    ctx = FakeContext()
    spinner = Spinner(200, 650, 450)
    spinner._fire_bullet(200, 650, 0)
    assert ctx.bullets == []
    run(spinner, ctx, 8.0)
    assert ctx.bullets
