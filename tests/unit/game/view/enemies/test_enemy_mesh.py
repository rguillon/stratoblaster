"""Unit tests of `src/game/view/enemies/enemy_mesh.py`."""

from types import SimpleNamespace

import pytest

from game.view.enemies import enemy_mesh
from game.view.enemies.enemy_mesh import (
    Wing,
    WingParts,
    collect_parts,
    flutter_animation,
    wing_parts_new,
)
from game.view.enemies.living_motion import flutter_angle
from render.geometry.solids import SolidBuilder


def _draw_everything(p) -> None:
    p.hull.box([1, 1, 1], [0, 0, 0])
    p.flesh.box([1, 1, 1], [0, 0, 0])
    p.neon.box([1, 1, 1], [1, 0, 0])
    p.reactor([0, 0, -4], 1.0)
    p.rotor([2, 0, 0], 2.1)
    p.rotor([-2, 0, 0], 2.1)
    p.muzzle([0, 0, 5], "gun")
    p.muzzle([1, 0, 5], "cannon")
    p.muzzle([2, 0, 5], None)
    p.flap([1, 0, 0], 1, 3.0, lambda w: w.flesh.box([1, 1, 1], [0, 0, 0]))


def test_collect_parts_gathers_the_reactors_rotors_muzzles_and_wings_of_a_drawing():
    collected = collect_parts(_draw_everything)
    assert [r.at for r in collected["reactors"]] == [[0, 0, -4]]
    assert [r.radius for r in collected["reactors"]] == [1.0]
    assert [r.at for r in collected["rotors"]] == [[2, 0, 0], [-2, 0, 0]]
    assert len(collected["wings"]) == 1
    assert collected["muzzles"] == [[[0, 0, 5], "gun"], [[1, 0, 5], "cannon"], [[2, 0, 5], "gun"]]


def test_collect_parts_keeps_the_body_builders_with_their_geometry():
    parts = collect_parts(_draw_everything)["parts"]
    assert len(parts.hull.geometry.positions) > 0
    assert len(parts.flesh.geometry.positions) > 0
    assert len(parts.neon.geometry.positions) > 0
    # Nothing was drawn as a charge light, nor on the vein.
    assert len(parts.charge.geometry.positions) == 0
    assert len(parts.vein.geometry.positions) == 0


def test_collect_parts_draws_a_wing_on_its_own_builders_with_its_hinge_and_span():
    collected = collect_parts(_draw_everything)
    wing = collected["wings"][0]
    assert isinstance(wing, Wing)
    assert wing.pivot == [1, 0, 0]
    assert wing.side == 1
    assert wing.span == 3.0
    assert len(wing.parts.flesh.geometry.positions) > 0


def test_collect_parts_of_an_empty_drawing_is_empty():
    collected = collect_parts(lambda p: None)
    assert collected["reactors"] == []
    assert collected["rotors"] == []
    assert collected["wings"] == []
    assert collected["muzzles"] == []
    assert len(collected["parts"].charge.geometry.positions) == 0


def test_wing_parts_new_is_four_empty_solid_builders():
    parts = wing_parts_new()
    assert isinstance(parts, WingParts)
    for builder in (parts.hull, parts.flesh, parts.neon, parts.vein):
        assert isinstance(builder, SolidBuilder)
        assert len(builder.geometry.positions) == 0


def test_p16_r07_flutter_animation_rolls_the_wing_node_as_the_clock_says():
    node = SimpleNamespace(rotation=SimpleNamespace(z=0.0))
    clock = [0.0]
    animate = flutter_animation(node, -1, 5.0, clock)
    clock[0] = 0.3
    animate(0.016)
    assert node.rotation.z == pytest.approx(flutter_angle(-1, 5.0, 0.3))


def test_p16_r07_the_flutter_clock_is_read_at_each_frame_not_when_made():
    node = SimpleNamespace(rotation=SimpleNamespace(z=0.0))
    clock = [0.0]
    animate = flutter_animation(node, 1, 0.5, clock)
    animate(0)
    assert node.rotation.z == pytest.approx(0)
    clock[0] = 0.1
    animate(0)
    assert node.rotation.z == pytest.approx(flutter_angle(1, 0.5, 0.1))


def test_enemy_parts_store_the_builders_they_are_given():
    builders = [object() for _ in range(9)]
    parts = enemy_mesh.EnemyParts(*builders)
    assert parts.hull is builders[0]
    assert parts.muzzle is builders[8]
