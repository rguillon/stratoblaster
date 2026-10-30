"""Unit tests of `src/game/sim/enemies/hydra.py`."""

import math

from helpers.enemy_steps import area, run
from helpers.fakes import FakeContext

from game.sim.enemy_kinds import ENEMY_KINDS

KIND = next(kind for kind in ENEMY_KINDS if kind.id == "hydra")

# BUG: the Hydra's necks are config joints (camelCase `amplitudeDeg`), which core's BossJoints reads
# as `amplitude_deg`: None under CPython (NaN angles in the browser). See test_juggernaut.py.


def test_p05_r19_the_kind_spawns_live_enemies_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert enemies
    for enemy in enemies:
        assert enemy.health > 0
        assert math.isfinite(enemy.x) and math.isfinite(enemy.y)
        assert enemy.y >= 600 or enemy.y <= 600


def test_p05_r19_a_spawned_enemy_moves_and_stays_finite_over_a_long_run() -> None:
    ctx = FakeContext()
    enemy = KIND.spawn(area(width=400, height=600))[0]
    start = (enemy.x, enemy.y)
    run(enemy, ctx, 8.0)
    assert math.isfinite(enemy.x) and math.isfinite(enemy.y)
    assert (enemy.x, enemy.y) != start
