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


class FakeBatch:
    """A batch of the flame layer: the instances added to it."""

    def __init__(self) -> None:
        self.added: list[tuple[Any, ...]] = []

    def add(self, world: Any, scale: list[float], along: float, color: Any, alpha: float) -> None:
        self.added.append((world, list(scale), along, color, alpha))


class FakeLayer:
    """The scene's flame layer: its batches by what was asked for, and the flames added."""

    def __init__(self) -> None:
        self.cone_batches: dict[int, FakeBatch] = {}
        self.puff_batches: dict[int, FakeBatch] = {}
        self.flames: list[Any] = []

    def cones(self, sides: int) -> FakeBatch:
        return self.cone_batches.setdefault(sides, FakeBatch())

    def puffs(self, kind: int) -> FakeBatch:
        return self.puff_batches.setdefault(kind, FakeBatch())

    def add(self, flame: Any) -> None:
        self.flames.append(flame)


@pytest.fixture
def flame_scene(monkeypatch: Any) -> SimpleNamespace:
    """Record the scene's flame layer and the model animations."""
    made = SimpleNamespace(layer=FakeLayer(), scenes=[], animations=[])

    def layer_of(scene: Any) -> FakeLayer:
        made.scenes.append(scene)
        return made.layer

    monkeypatch.setattr(reactor_flame, "flame_layer", layer_of)
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
HEAVY_SIZE = {"nozzleZ": -1.0, "length": 4.0, "diameter": 2.0, "puffDiameter": 1.0, "sides": 8}
ENEMY_COLORS = reactor_flame.FlameColors([1, 0, 0, 0.5], [1, 0.5, 0.5, 0.8], [1, 0, 0, 0.6])
WORLD = "world-matrix"


def test_d428_a_flame_has_no_mesh_it_joins_its_scene_s_flame_layer(
    flame_scene: SimpleNamespace,
) -> None:
    parent = MagicMock(name="parent")
    flame = reactor_flame.build_reactor_flame("gnat-reactor", LIGHT_SIZE, parent, ENEMY_COLORS)
    assert flame_scene.scenes == [parent.getScene()]
    assert flame_scene.layer.flames == [flame]
    # It shows whenever the node it hangs from does.
    assert flame.node is parent


def test_enm_40_an_enemy_flame_is_two_cones_and_few_tetrahedra_in_its_colours(
    flame_scene: SimpleNamespace,
) -> None:
    flame = reactor_flame.build_reactor_flame("gnat-reactor", LIGHT_SIZE, MagicMock(), ENEMY_COLORS)
    flame.write(WORLD)
    layer = flame_scene.layer
    # Cones of the flame's sides; tetrahedra for a light flame, as many as it asks for.
    assert list(layer.cone_batches) == [6]
    assert list(layer.puff_batches) == [reactor_flame.TETRAHEDRON]
    outer, inner = layer.cone_batches[6].added
    puffs = layer.puff_batches[reactor_flame.TETRAHEDRON].added
    assert len(puffs) == 2
    assert outer[3] == ENEMY_COLORS.exhaust
    assert inner[3] == ENEMY_COLORS.flame
    assert all(puff[3] == ENEMY_COLORS.plasma for puff in puffs)
    assert all(entry[0] == WORLD for entry in [outer, inner, *puffs])


def test_gfx_ship_06_a_player_flame_is_blue_with_icosahedra(flame_scene: SimpleNamespace) -> None:
    """Also GFX-ART-04: the ship look's colours and opacities."""
    flame = reactor_flame.build_reactor_flame("engine", HEAVY_SIZE, MagicMock())
    flame.write(WORLD)
    layer = flame_scene.layer
    assert list(layer.cone_batches) == [8]
    puffs = layer.puff_batches[reactor_flame.ICOSAHEDRON].added
    assert len(puffs) == reactor_flame.FLAME.puffCount
    look = reactor_flame.SHIP_LOOK
    outer, inner = layer.cone_batches[8].added
    assert outer[3] == [*look.reactorExhaust.emissive, look.reactorExhaust.alpha]
    assert inner[3] == [*look.reactorFlame.emissive, look.reactorFlame.alpha]
    assert puffs[0][3] == [*look.reactorPlasma.emissive, look.reactorPlasma.alpha]


def test_gfx_ship_06_the_cones_start_at_the_nozzle_and_flicker_round_their_size(
    flame_scene: SimpleNamespace,
) -> None:
    flame = reactor_flame.build_reactor_flame("gnat-reactor", LIGHT_SIZE, MagicMock(), ENEMY_COLORS)
    flame.write(WORLD)
    outer, inner = flame_scene.layer.cone_batches[6].added
    look = reactor_flame.FLAME
    for cone, width, length in [
        (outer, LIGHT_SIZE["diameter"], LIGHT_SIZE["length"]),
        (inner, LIGHT_SIZE["diameter"] * look.coreWidth, LIGHT_SIZE["length"] * look.coreLength),
    ]:
        scale = cone[1]
        # Round at the nozzle, as wide and long as its size, give or take the flicker.
        assert scale[0] == scale[1]
        assert scale[0] == pytest.approx(width, rel=look.widthFlicker + 1e-9)
        assert scale[2] == pytest.approx(length, rel=look.lengthFlicker + 1e-9)
        assert cone[2] == LIGHT_SIZE["nozzleZ"]
    # Its opacity dims with the flicker, never above the colour's own.
    assert 0.5 * (1 - look.brightnessFlicker) <= outer[4] <= 0.5
    assert 0.8 * (1 - look.brightnessFlicker) <= inner[4] <= 0.8


def test_gfx_art_11_the_flame_lives_on_the_frames_time(flame_scene: SimpleNamespace) -> None:
    parent = MagicMock(name="parent")
    flame = reactor_flame.build_reactor_flame("gnat-reactor", LIGHT_SIZE, parent, ENEMY_COLORS)
    node, on_frame = flame_scene.animations[0]
    assert node is parent
    puffs = flame_scene.layer.puff_batches[reactor_flame.TETRAHEDRON]
    # Built at time 0: the first puff sits at the nozzle, at full size and see-through.
    flame.write(WORLD)
    first = puffs.added[0]
    radius = LIGHT_SIZE["puffDiameter"] / 2
    assert first[1] == pytest.approx([radius, radius, radius * 1.6])
    assert first[2] == pytest.approx(LIGHT_SIZE["nozzleZ"] - 0.01)
    assert first[4] == 0
    # The clock adds up the frames' times: the puff has moved down the exhaust and shrunk.
    on_frame(0.25)
    on_frame(0.25)
    assert flame.time == pytest.approx(0.5)
    puffs.added.clear()
    flame.write(WORLD)
    progress = reactor_flame.puff_progress(0.5, 0, 2, reactor_flame.FLAME.puffSpeed)
    moved = puffs.added[0]
    assert moved[2] == pytest.approx(LIGHT_SIZE["nozzleZ"] - 0.01 - progress * LIGHT_SIZE["length"])
    assert moved[1][0] == pytest.approx(radius * (1 - 0.7 * progress))
    assert moved[4] == pytest.approx(0.6 * reactor_flame.puff_opacity(progress))
