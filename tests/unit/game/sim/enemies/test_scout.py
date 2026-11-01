"""Unit tests of `src/game/sim/enemies/scout.py`."""

import pytest
from helpers.enemy_steps import run
from helpers.fakes import FakeContext

from game.config.enemies import ENEMY_CONFIG
from game.sim.enemies.scout import Scout

CFG = ENEMY_CONFIG.scout


def test_enm_scout_05_a_scout_flies_straight_down_at_its_speed() -> None:
    scout = Scout(200, 500)
    run(scout, FakeContext(), 1.0)
    assert scout.x == 200
    assert scout.y == pytest.approx(500 - CFG.speed, rel=1e-6)


def test_enm_scout_06_a_scout_fires_an_aimed_bullet_each_fire_interval_on_the_playfield() -> None:
    ctx = FakeContext()
    scout = Scout(200, 300)
    run(scout, ctx, 6.0)
    assert len(ctx.bullets) >= 3
    assert all(spec is CFG.bullet for *_, spec in ctx.bullets)


def test_enm_15_a_scout_above_the_playfield_does_not_fire() -> None:
    """Also ENM-SCOUT-06: it fires only over the playfield."""
    ctx = FakeContext()
    scout = Scout(200, 700)
    run(scout, ctx, 0.5)
    assert ctx.bullets == []


def test_enm_23_a_scout_charges_towards_its_next_shot() -> None:
    scout = Scout(200, 300)
    run(scout, FakeContext(), 0.5)
    assert 0 <= scout.charge <= 1
