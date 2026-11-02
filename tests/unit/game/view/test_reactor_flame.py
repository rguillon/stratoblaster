# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/reactor_flame.py` (GFX-SHIP-06, GFX-ART-11)."""

import math
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from game.view import reactor_flame
from game.view.reactor_flame import (
    _around,
    _dimmed,
    flicker,
    puff_opacity,
    puff_progress,
    reactor_phase,
)


@pytest.fixture(autouse=True)
def python_bit_helpers(monkeypatch: Any) -> None:
    """`Math.imul` and `charCodeAt` are JavaScript: their Python equivalents here."""

    def imul(a: Any, b: Any) -> Any:
        value = (a * b) & 0xFFFFFFFF
        return value - 2**32 if value >= 2**31 else value

    monkeypatch.setattr(reactor_flame, "_imul", imul)
    monkeypatch.setattr(reactor_flame, "_char_code", lambda text, index: ord(text[index]))


def test_the_flicker_is_the_mean_of_its_sines_in_the_unit_range() -> None:
    value = flicker(0.37, 1.2, [1.0, 2.5, 4.0])
    assert -1 <= value <= 1
    expected = (
        sum(math.sin(2 * math.pi * f * 0.37 + 1.2 * (i + 1)) for i, f in enumerate([1.0, 2.5, 4.0]))
        / 3
    )
    assert value == pytest.approx(expected)


def test_a_flicker_without_frequencies_is_still() -> None:
    assert flicker(5.0, 1.0, []) == 0


def test_a_flicker_with_one_frequency_is_a_sine() -> None:
    assert flicker(0.25, 0.0, [1.0]) == pytest.approx(1.0)


def test_reactors_of_different_names_do_not_flicker_in_step() -> None:
    a = reactor_phase("player-engine-left")
    b = reactor_phase("player-engine-right")
    assert 0 <= a < 2 * math.pi
    assert a != b


def test_a_reactors_phase_is_stable_for_its_name() -> None:
    assert reactor_phase("flame") == reactor_phase("flame")


def test_a_puff_travels_down_the_exhaust_and_starts_again() -> None:
    assert puff_progress(0.0, 0, 4, 1.0) == 0
    assert puff_progress(0.5, 0, 4, 1.0) == pytest.approx(0.5)
    assert puff_progress(0.0, 1, 4, 1.0) == pytest.approx(0.25)
    assert 0 <= puff_progress(123.456, 3, 4, 2.0) < 1


def test_a_puff_fades_in_near_the_nozzle_and_out_at_the_tip() -> None:
    assert puff_opacity(0) == 0
    assert puff_opacity(1) == 0
    assert puff_opacity(0.5) > 0
    assert puff_opacity(0.5) > puff_opacity(0.95)


def test_a_puff_is_at_most_fully_opaque() -> None:
    assert max(puff_opacity(p / 100) for p in range(101)) <= 1


def test_the_flicker_maps_to_a_factor_around_one() -> None:
    assert _around(0, 0.2) == 1
    assert _around(1, 0.2) == pytest.approx(1.2)
    assert _around(-1, 0.2) == pytest.approx(0.8)


def test_the_flicker_maps_to_a_visibility_that_only_dims() -> None:
    assert _dimmed(1, 0.5) == pytest.approx(1)
    assert _dimmed(-1, 0.5) == pytest.approx(0.5)
    assert _dimmed(0, 0.5) == pytest.approx(0.75)


@pytest.fixture
def flame_scene(monkeypatch: Any) -> SimpleNamespace:
    """Babylon stand-ins for a flame: the cylinders, puffs and pivots made, and its animation."""
    made = SimpleNamespace(cylinders=[], puffs=[], pivots=[], animations=[])

    def pivot(label: str, _scene: Any) -> Any:
        made.pivots.append(MagicMock(name=label))
        return made.pivots[-1]

    def cylinder(name: str, options: Any, _scene: Any) -> Any:
        made.cylinders.append(
            SimpleNamespace(name=name, options=options, mesh=MagicMock(name=name))
        )
        return made.cylinders[-1].mesh

    def polyhedron(name: str, options: Any, _scene: Any) -> Any:
        made.puffs.append(SimpleNamespace(name=name, options=options, mesh=MagicMock(name=name)))
        return made.puffs[-1].mesh

    monkeypatch.setattr(reactor_flame, "new_transform_node", pivot)
    monkeypatch.setattr(reactor_flame, "create_cylinder", cylinder)
    monkeypatch.setattr(reactor_flame, "create_polyhedron", polyhedron)
    # `{height, diameterTop, ...}` and `{type, size}` are JavaScript objects: plain ones here.
    monkeypatch.setattr(reactor_flame, "_cylinder_options", lambda h, _d, _t: SimpleNamespace(h=h))
    monkeypatch.setattr(reactor_flame, "_polyhedron_options", lambda kind, size: (kind, size))
    monkeypatch.setattr(
        reactor_flame, "babylon_class", lambda name: SimpleNamespace(NO_CAP="no-cap-" + name)
    )
    monkeypatch.setattr(
        reactor_flame,
        "add_model_animation",
        lambda node, anim: made.animations.append((node, anim)),
    )
    return made


LIGHT_SIZE = {
    "nozzleZ": -2.0,
    "length": 6.0,
    "diameter": 1.5,
    "puffDiameter": 0.8,
    "sides": 6,
    "light": {"puffs": 2},
}
ENEMY_MATERIALS = {"exhaust": "enemy-exhaust", "flame": "enemy-flame", "plasma": "enemy-plasma"}


def test_enm_40_an_enemy_flame_is_light_uncapped_cones_and_few_tetrahedra(
    flame_scene: SimpleNamespace,
) -> None:
    parent = MagicMock(name="parent")
    reactor_flame.build_reactor_flame("gnat-reactor", LIGHT_SIZE, parent, ENEMY_MATERIALS)
    outer, inner = flame_scene.cylinders
    assert (outer.name, inner.name) == ("gnat-reactor-exhaust", "gnat-reactor-flame")
    # No caps on the cones of a light flame.
    assert outer.options.cap == "no-cap-Mesh"
    assert inner.options.cap == "no-cap-Mesh"
    # Its own materials, not the player's blue.
    assert outer.mesh.material == "enemy-exhaust"
    assert inner.mesh.material == "enemy-flame"
    # As many puffs as the light flame asks for, each a tetrahedron.
    assert [p.name for p in flame_scene.puffs] == ["gnat-reactor-puff-0", "gnat-reactor-puff-1"]
    assert all(p.options == (reactor_flame.TETRAHEDRON, 0.4) for p in flame_scene.puffs)
    assert all(p.mesh.material == "enemy-plasma" for p in flame_scene.puffs)
    assert all(p.mesh.parent is parent for p in flame_scene.puffs)


def test_gfx_ship_06_the_cones_point_back_from_the_nozzle(flame_scene: SimpleNamespace) -> None:
    parent = MagicMock(name="parent")
    reactor_flame.build_reactor_flame("gnat-reactor", LIGHT_SIZE, parent, ENEMY_MATERIALS)
    outer_pivot = flame_scene.pivots[0]
    outer = flame_scene.cylinders[0].mesh
    assert outer_pivot.parent is parent
    assert outer.parent is outer_pivot
    assert outer.rotation.x == pytest.approx(-math.pi / 2)
    assert outer.position.z == pytest.approx(-LIGHT_SIZE["length"] / 2)
    assert all(p.position.z == LIGHT_SIZE["nozzleZ"] for p in flame_scene.pivots)
    assert outer.isPickable is False


def test_gfx_art_11_the_flame_lives_on_the_frames_time(flame_scene: SimpleNamespace) -> None:
    parent = MagicMock(name="parent")
    reactor_flame.build_reactor_flame("gnat-reactor", LIGHT_SIZE, parent, ENEMY_MATERIALS)
    node, on_frame = flame_scene.animations[0]
    assert node is parent
    puff = flame_scene.puffs[0].mesh
    # Built at time 0: the first puff sits at the nozzle.
    assert puff.position.z == pytest.approx(LIGHT_SIZE["nozzleZ"] - 0.01)
    on_frame(0.25)
    progress = reactor_flame.puff_progress(0.25, 0, 2, reactor_flame.FLAME.puffSpeed)
    expected = LIGHT_SIZE["nozzleZ"] - 0.01 - progress * LIGHT_SIZE["length"]
    assert puff.position.z == pytest.approx(expected)
    assert puff.visibility == pytest.approx(reactor_flame.puff_opacity(progress))
    # The clock adds up the frames' times.
    on_frame(0.25)
    progress = reactor_flame.puff_progress(0.5, 0, 2, reactor_flame.FLAME.puffSpeed)
    assert puff.visibility == pytest.approx(reactor_flame.puff_opacity(progress))
