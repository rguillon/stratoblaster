"""Unit tests of `src/game/view/enemies/blast_particles.py`."""

import math
from types import SimpleNamespace

import pytest

from core.math.rng import create_rng
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import blast_particles as bp
from game.view.enemies.blast_particles import (
    BLAST_LAYERS,
    BlastParticles,
    Particle,
    look_debris,
    look_embers,
    look_fireballs,
    look_rings,
    look_smoke,
    ramp,
)

LOOK = ENEMY_LOOK.blasts


def _particle(**overrides) -> Particle:
    fields = dict(
        x=0.0,
        y=0.0,
        vx=0.0,
        vy=0.0,
        size=2.0,
        life=1.0,
        growth=1.0,
        drag=0.0,
        ember=0.0,
        wisp=0.0,
        small=1.0,
        age=0.0,
    )
    fields.update(overrides)
    return Particle(**fields)


def _blast(x=0.0, y=0.0, radius=10.0, kind="enemy") -> SimpleNamespace:
    return SimpleNamespace(x=x, y=y, radius=radius, kind=kind)


def test_ramp_walks_the_colours_in_order_and_clamps_at_the_ends():
    colours = [[0, 0, 0], [1, 0, 0], [1, 1, 0]]
    assert ramp(colours, 0) == pytest.approx([0, 0, 0])
    assert ramp(colours, 1) == pytest.approx([1, 1, 0])
    assert ramp(colours, 0.25) == pytest.approx([0.5, 0, 0])
    assert ramp(colours, 0.75) == pytest.approx([1, 0.5, 0])
    assert ramp(colours, -3) == pytest.approx([0, 0, 0])
    assert ramp(colours, 7) == pytest.approx([1, 1, 0])


def test_ramp_of_a_single_colour_is_that_colour():
    assert ramp([[0.2, 0.4, 0.6]], 0.5) == pytest.approx([0.2, 0.4, 0.6])


def test_particle_grows_from_its_size_to_its_growth_across_its_life():
    p = _particle(size=2.0, growth=3.0)
    assert bp.grown(p, 0) == pytest.approx(2.0)
    assert bp.grown(p, 1) == pytest.approx(6.0)
    assert bp.grown(p, 0.5) == pytest.approx(4.0)


def test_shock_ring_expands_with_the_square_root_of_its_age_and_fades_quadratically():
    p = _particle(size=4.0)
    early = look_rings(p, 0.25)
    assert early.radius == pytest.approx(4.0 * 0.5)
    assert early.a == pytest.approx(0.75**2)
    assert (early.r, early.g, early.b) == pytest.approx(tuple(LOOK.ring.color))
    assert look_rings(p, 1).a == pytest.approx(0)


def test_fireball_is_opaque_then_fades_out_after_its_opaque_share_of_life():
    f = LOOK.fireball
    p = _particle(size=2.0)
    assert look_fireballs(p, 0).a == pytest.approx(f.alpha)
    # Still opaque at the end of the opaque share, and gone at the end of life.
    assert look_fireballs(p, f.opaque).a == pytest.approx(f.alpha)
    assert look_fireballs(p, 1).a == pytest.approx(0)
    assert look_fireballs(p, (1 + f.opaque) / 2).a == pytest.approx(f.alpha / 2, rel=1e-6)


def test_fireball_cools_from_white_hot_to_deep_red():
    colours = LOOK.fireball.colors
    assert look_fireballs(_particle(), 0).r == pytest.approx(colours[0][0])
    assert look_fireballs(_particle(), 1).r == pytest.approx(colours[-1][0])


def test_smoke_thickens_then_thins_out_as_it_spreads():
    p = _particle(size=1.0, growth=2.0)
    assert look_smoke(p, 0).a == pytest.approx(0)
    peak = look_smoke(p, 0.12).a
    assert peak == pytest.approx(LOOK.smoke.alpha * (1 - 0.12))
    assert look_smoke(p, 0.5).a < peak
    assert look_smoke(p, 1).a == pytest.approx(0)


def test_debris_shrinks_to_half_and_cools_while_it_burns():
    p = _particle(size=4.0)
    assert look_debris(p, 0).radius == pytest.approx(4.0)
    assert look_debris(p, 1).radius == pytest.approx(2.0)


def test_embers_shrink_to_nothing():
    p = _particle(size=4.0)
    assert look_embers(p, 0).radius == pytest.approx(4.0)
    assert look_embers(p, 1).radius == pytest.approx(0)


def test_the_layers_have_one_look_each_in_draw_order():
    assert BLAST_LAYERS == ["smoke", "rings", "fireballs", "debris", "embers"]
    assert set(bp.LOOKS) == set(BLAST_LAYERS)


def test_count_of_is_clamped_scaled_rounded_and_at_least_one():
    blasts = BlastParticles(create_rng(1))
    assert blasts.count_of(100, [2, 5], 1) == 5
    assert blasts.count_of(0, [2, 5], 1) == 2
    assert blasts.count_of(3, [2, 5], 0.5) == 2
    assert blasts.count_of(0, [0, 0], 0) == 1


def test_direction_has_the_length_asked_for_in_a_random_direction():
    blasts = BlastParticles(create_rng(7))
    for _ in range(20):
        v = blasts.direction(3.0)
        assert math.hypot(*v) == pytest.approx(3.0)


def test_add_starts_a_particle_behind_its_delay_and_respects_the_cap(monkeypatch):
    monkeypatch.setattr(bp.LOOK, "cap", 2)
    blasts = BlastParticles(create_rng(1))
    blasts.add("smoke", {"x": 1, "y": 2, "size": 3, "life": 1, "delay": 0.5})
    (p,) = blasts.layers["smoke"]
    assert (p.x, p.y, p.size) == (1, 2, 3)
    assert p.age == pytest.approx(-0.5)
    assert p.growth == 1 and p.drag == 0
    blasts.add("smoke", {"x": 0, "y": 0, "size": 1, "life": 1})
    blasts.add("smoke", {"x": 0, "y": 0, "size": 1, "life": 1})
    assert len(blasts.layers["smoke"]) == 2


def test_step_ages_particles_and_drops_the_finished_ones():
    blasts = BlastParticles(create_rng(1))
    blasts.add("rings", {"x": 0, "y": 0, "size": 1, "life": 0.5})
    out = blasts.step(0.2)
    assert len(out["rings"]) == 1
    assert blasts.layers["rings"][0].age == pytest.approx(0.2)
    blasts.step(0.4)
    assert blasts.layers["rings"] == []


def test_a_particle_still_waiting_to_appear_is_not_drawn_yet():
    blasts = BlastParticles(create_rng(1))
    blasts.add("rings", {"x": 0, "y": 0, "size": 1, "life": 1, "delay": 0.5})
    out = blasts.step(0.1)
    assert out["rings"] == []
    assert len(blasts.layers["rings"]) == 1


def test_drag_slows_a_moving_particle_and_moves_it_on():
    blasts = BlastParticles(create_rng(1))
    blasts.add("debris", {"x": 0, "y": 0, "size": 1, "life": 10, "vx": 10, "vy": 0, "drag": 1})
    blasts.step(0.1)
    (p,) = blasts.layers["debris"]
    slow = math.exp(-0.1)
    assert p.vx == pytest.approx(10 * slow)
    assert p.x == pytest.approx(10 * slow * 0.1)


def test_an_enemy_blast_throws_a_ring_fireballs_debris_and_embers():
    blasts = BlastParticles(create_rng(3))
    blasts.emit(_blast(x=5, y=6, radius=10))
    assert len(blasts.layers["rings"]) == 1
    assert len(blasts.layers["fireballs"]) >= 2
    assert len(blasts.layers["debris"]) >= 1
    assert len(blasts.layers["embers"]) >= 1
    # The ring starts on the blast's centre.
    ring = blasts.layers["rings"][0]
    assert (ring.x, ring.y) == (5, 6)


def test_a_missile_blast_is_smaller_and_throws_fewer_pieces():
    enemy = BlastParticles(create_rng(3))
    missile = BlastParticles(create_rng(3))
    enemy.emit(_blast(radius=20))
    missile.emit(_blast(radius=20, kind="missile"))
    assert missile.count() < enemy.count()
    assert missile.layers["rings"][0].size < enemy.layers["rings"][0].size


def test_a_blast_is_never_drawn_bigger_than_the_largest_radius():
    capped = BlastParticles(create_rng(3))
    huge = BlastParticles(create_rng(3))
    capped.emit(_blast(radius=LOOK.maxRadius))
    huge.emit(_blast(radius=LOOK.maxRadius * 10))
    assert capped.layers["rings"][0].size == pytest.approx(huge.layers["rings"][0].size)


def test_burning_debris_drops_embers_while_it_is_hot():
    blasts = BlastParticles(create_rng(5))
    blasts.add(
        "debris",
        {"x": 0, "y": 0, "size": 1, "life": 1, "ember": 0, "wisp": 0, "small": 1},
    )
    blasts.burn(0.01)
    assert len(blasts.layers["embers"]) == 1
    assert len(blasts.layers["smoke"]) == 1


def test_burnt_out_debris_drops_nothing():
    blasts = BlastParticles(create_rng(5))
    blasts.add("debris", {"x": 0, "y": 0, "size": 1, "life": 1, "ember": 0, "wisp": 0})
    blasts.layers["debris"][0].age = 0.9  # past BURN_LIMIT of its life
    blasts.burn(0.01)
    assert blasts.layers["embers"] == []
    assert blasts.layers["smoke"] == []


def test_count_sums_every_layer():
    blasts = BlastParticles(create_rng(2))
    blasts.add("rings", {"x": 0, "y": 0, "size": 1, "life": 1})
    blasts.add("embers", {"x": 0, "y": 0, "size": 1, "life": 1})
    assert blasts.count() == 2
