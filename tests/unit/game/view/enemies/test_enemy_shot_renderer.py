"""Unit tests of `src/game/view/enemies/enemy_shot_renderer.py`."""

from types import SimpleNamespace

import pytest

from game.config.enemy_look import ENEMY_LOOK
from game.config.readability import READABILITY
from game.view.enemies import enemy_shot_renderer as sr

BULLETS = ENEMY_LOOK.bullets


def test_disc_alphas_are_the_centre_then_each_ring_at_its_fade():
    # The centre vertex is one vertex; each further ring has `segments` vertices.
    alphas = sr.disc_alphas(4, [1.0, 0.5, 0.0])
    assert alphas == [1.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0]


def test_disc_with_no_rings_has_no_vertices():
    assert sr.disc_alphas(8, []) == []


def test_halo_flickers_around_its_size_at_its_flicker_rate():
    halo = BULLETS.halo
    assert sr.halo_scale(0) == pytest.approx(halo.size)
    quarter = 1 / (4 * halo.flickerHz)
    assert sr.halo_scale(quarter) == pytest.approx(halo.size * (1 + halo.flicker))
    assert sr.halo_scale(3 * quarter) == pytest.approx(halo.size * (1 - halo.flicker))


def test_core_pulses_around_its_size_at_its_pulse_rate():
    core = BULLETS.core
    assert sr.core_scale(0) == pytest.approx(core.size)
    quarter = 1 / (4 * core.pulse.hz)
    assert sr.core_scale(quarter) == pytest.approx(core.size * (1 + core.pulse.amount))


def test_drawn_radius_follows_the_bullet_but_never_goes_under_half_the_minimum_size():
    minimum = READABILITY.minEnemyBulletSize
    big = SimpleNamespace(radius=10)
    tiny = SimpleNamespace(radius=0.0001)
    assert sr.drawn_radius(big) == pytest.approx(10 * BULLETS.scale)
    assert sr.drawn_radius(tiny) == pytest.approx(minimum / 2)


def test_placements_scale_the_radius_by_the_layer_rule():
    b = SimpleNamespace(age=0.0, heading=0.0)
    assert sr.body_placement(b, 2.0) == pytest.approx([2.0, 0])
    assert sr.halo_placement(b, 2.0) == pytest.approx([2.0 * BULLETS.halo.size, 0])
    assert sr.core_placement(b, 2.0) == pytest.approx([2.0 * BULLETS.core.size, 0])
    assert sr.fixed_placement(0.25)(b, 4.0) == pytest.approx([1.0, 0])


def test_swirl_grows_with_its_size_and_turns_with_heading_and_age():
    swirl = SimpleNamespace(size=0.5, spinRadPerSec=2.0)
    b = SimpleNamespace(age=0.5, heading=1.0)
    place = sr.swirl_placement(swirl)
    assert place(b, 10.0) == pytest.approx([5.0, 1.0 * 3 + 2.0 * 0.5])
