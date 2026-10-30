"""Unit tests of `src/game/sim/enemies/enemy_helpers.py`."""

import pytest
from helpers.enemy_steps import area
from helpers.fakes import FakeContext

from core.math.rng import create_rng
from game.sim.enemies.enemy_helpers import (
    Cadence,
    bullet_shot,
    clamp_entry,
    coin,
    on_playfield,
    pick_x,
    playfield_path,
    range_in,
    top_bounds,
    top_x,
)


class _Enemy:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def test_cadence_fires_every_interval_and_reports_the_count_of_a_long_step() -> None:
    gun = Cadence(1.0, 0.5)
    assert gun.tick(0.4) == 0
    assert gun.tick(0.2) == 1
    assert gun.tick(2.0) == 2


def test_cadence_progress_is_the_fraction_of_the_wait_done() -> None:
    gun = Cadence(2.0)
    assert gun.progress == pytest.approx(0)
    gun.tick(0.5)
    assert gun.progress == pytest.approx(0.25)


def test_on_playfield_is_inclusive_of_its_edges() -> None:
    ctx = FakeContext()
    assert on_playfield(_Enemy(0, 0), ctx)
    assert on_playfield(_Enemy(ctx.width, ctx.height), ctx)
    assert not on_playfield(_Enemy(-1, 10), ctx)
    assert not on_playfield(_Enemy(10, ctx.height + 1), ctx)


def test_clamp_entry_keeps_a_position_away_from_the_corners() -> None:
    assert clamp_entry(0.0) == pytest.approx(0.08)
    assert clamp_entry(1.0) == pytest.approx(0.92)
    assert clamp_entry(0.5) == 0.5


def test_coin_is_heads_below_one_half() -> None:
    assert coin(lambda: 0.2) is True
    assert coin(lambda: 0.7) is False


def test_top_bounds_is_the_whole_width_unless_a_top_range_is_given() -> None:
    assert top_bounds(area(width=400)) == (0, 400)
    assert top_bounds(area(top_range=(50, 300))) == (50, 300)


def test_top_x_maps_a_fraction_across_the_top_range() -> None:
    a = area(top_range=(100, 300))
    assert top_x(a, 0) == 100
    assert top_x(a, 0.5) == 200
    assert top_x(a, 1) == 300


def test_range_in_maps_a_random_draw_into_the_range() -> None:
    assert range_in(lambda: 0.0, (0.2, 0.6)) == pytest.approx(0.2)
    assert range_in(lambda: 0.5, (0.2, 0.6)) == pytest.approx(0.4)


def test_pick_x_draws_a_fraction_of_the_range_across_the_top() -> None:
    a = area(width=400)
    rng = create_rng(3)
    x = pick_x(rng, (0.25, 0.75), a)
    assert 100 <= x <= 300


def test_playfield_path_mirrors_its_x_fractions_when_asked() -> None:
    a = area(width=400, height=600)
    straight = playfield_path([[0.25, 0.5], [0.25, 1.0]], a, False)
    mirrored = playfield_path([[0.25, 0.5], [0.25, 1.0]], a, True)
    assert straight.at(0).x == pytest.approx(100)
    assert mirrored.at(0).x == pytest.approx(300)
    assert straight.at(0).y == pytest.approx(300)


def test_bullet_shot_fires_the_bullet_of_the_enemy_at_each_shot() -> None:
    ctx = FakeContext()
    spec = object()
    bullet_shot(ctx, spec)(1.0, 2.0, 0.5)
    assert ctx.bullets == [(1.0, 2.0, 0.5, spec)]
