# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/shots/laser_particles.py`."""

from types import SimpleNamespace
from typing import Any

import pytest

from core.math.rng import create_rng
from game.view.shots.laser_particles import LaserParticles

OPTIONS = SimpleNamespace(count=6, speed=[50, 80], radius=[1, 2], spread=0.8, seed=4)


def segment(y0: Any, y1: Any, x: Any = 0.0, width: Any = 10.0, hit: Any = False) -> Any:
    return SimpleNamespace(x=x, y0=y0, y1=y1, width=width, hit=hit)


def test_gfx_shot_03_the_particles_start_spread_along_the_beam() -> None:
    particles = LaserParticles(OPTIONS, create_rng(1), 100.0)
    assert len(particles._particles) == OPTIONS.count
    assert all(0 <= p.distance < 100 for p in particles._particles)
    assert all(-1 <= p.lateral <= 1 for p in particles._particles)
    assert all(50 <= p.speed <= 80 for p in particles._particles)


def test_gfx_shot_03_no_beam_no_particles() -> None:
    particles = LaserParticles(OPTIONS, create_rng(1), 100.0)
    assert particles.step([], 0.1) == []


def test_gfx_shot_03_a_beam_of_no_length_draws_nothing() -> None:
    particles = LaserParticles(OPTIONS, create_rng(1), 100.0)
    assert particles.step([segment(5, 5)], 0.1) == []


def test_gfx_shot_03_particles_wrap_around_the_beam_and_stay_on_it() -> None:
    particles = LaserParticles(OPTIONS, create_rng(2), 100.0)
    beam = [segment(0, 40, x=3.0), segment(40, 120, x=4.0, width=4.0)]
    spots = particles.step(beam, 10.0)
    assert len(spots) == OPTIONS.count
    for s in spots:
        assert 0 <= s.y <= 120
        assert s.radius > 0


def test_gfx_shot_03_each_particle_is_drawn_inside_the_width_of_its_segment() -> None:
    particles = LaserParticles(OPTIONS, create_rng(7), 100.0)
    beam = [segment(0, 100, x=20.0, width=10.0)]
    for s in particles.step(beam, 0.0):
        assert abs(s.x - 20.0) <= 10.0 * OPTIONS.spread / 2 + 1e-9


def test_gfx_shot_03_the_particles_spread_over_the_drawn_width() -> None:
    """With a width bonus, the particles spread over the hit width plus the bonus."""
    narrow = LaserParticles(OPTIONS, create_rng(7), 100.0).step([segment(0, 100)], 0.0)
    wide = LaserParticles(OPTIONS, create_rng(7), 100.0, 10.0).step([segment(0, 100)], 0.0)
    for a, b in zip(narrow, wide, strict=True):
        assert b.x == pytest.approx(2 * a.x)


def test_gfx_shot_03_a_particle_moves_up_the_beam_by_its_speed() -> None:
    particles = LaserParticles(OPTIONS, create_rng(3), 100.0)
    p = particles._particles[0]
    p.distance = 10.0
    p.speed = 5.0
    beam = [segment(0, 100)]
    spot = particles.step(beam, 2.0)[0]
    assert spot.y == pytest.approx(0 + 10.0 + 10.0)
