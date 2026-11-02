# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/blast_renderer.py`: the blast layers' discs and meshes."""

from types import SimpleNamespace
from typing import Any, ClassVar
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon
from helpers.render_fakes import FakeTypedArray

from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.enemies import blast_renderer as br
from game.view.enemies.blast_particles import BLAST_LAYERS, BlastSpot

LOOK = ENEMY_LOOK.blasts


def _rgb(geo: Any, i: int) -> list[float]:
    """Return the RGB of vertex `i` of a coloured geometry."""
    return geo.colors[4 * i : 4 * i + 3]


def _alpha(geo: Any, i: int) -> float:
    alpha: float = geo.colors[4 * i + 3]
    return alpha


def test_object_with_colors_copies_a_geometry_with_other_colours() -> None:
    geo = record({"positions": [1, 2, 3], "indices": [0], "colors": [0, 0, 0, 1]})
    copy = br._object_with_colors(geo, [1, 1, 1, 0.5])
    assert copy.colors == [1, 1, 1, 0.5]
    assert copy.positions == [1, 2, 3]
    assert copy.indices == [0]
    # The geometry it copies keeps its own colours.
    assert geo.colors == [0, 0, 0, 1]


def test_float32_array_falls_back_to_a_zero_filled_list_in_cpython() -> None:
    """The `__pragma__("skip")` body CPython runs: a list of zeros, not a typed array."""
    assert br._float32_array(2) == [0.0, 0.0]
    assert br._float32_array(0) == []


@pytest.mark.parametrize(("n", "expected"), [(0, 0), (1, 0), (2, 1), (5, 3), (16, 4), (17, 5)])
def test_ceil_log2_is_the_power_of_two_a_count_rounds_up_to(n: int, expected: int) -> None:
    assert br._ceil_log2(n) == expected


def test_gfx_fx_05_a_soft_disc_is_white_at_its_centre_and_fades_to_black() -> None:
    geo = br.soft(8)
    # The centre, then one ring of 8 vertices per colour after the first.
    assert len(geo.colors) // 4 == 1 + 3 * 8
    assert _rgb(geo, 0) == [1, 1, 1]
    assert _rgb(geo, 1) == [0.85, 0.85, 0.85]
    assert _rgb(geo, 3 * 8) == [0, 0, 0]


def test_gfx_fx_05_a_ring_is_lit_only_at_its_rim() -> None:
    """Black (nothing, added on) inside and out: only its rim shows."""
    geo = br.ring(6)
    count = len(geo.colors) // 4
    assert count == 1 + 9 * 6
    lit = [i for i in range(count) if _rgb(geo, i) != [0, 0, 0]]
    # The grey ring then the white ring, 6 vertices each, just inside the black edge.
    assert lit == list(range(1 + 6 * 6, 1 + 8 * 6))
    assert _rgb(geo, 1 + 7 * 6) == [1, 1, 1]


def test_gfx_fx_07_a_puff_of_smoke_is_white_its_opacity_fading_to_the_rim() -> None:
    soft = br.soft(8)
    geo = br.puff(8)
    count = len(geo.colors) // 4
    assert geo.positions == soft.positions
    assert geo.indices == soft.indices
    assert all(_rgb(geo, i) == [1, 1, 1] for i in range(count))
    # Its opacity is the soft disc's brightness: opaque at the centre, clear at the rim.
    assert [_alpha(geo, i) for i in range(count)] == [soft.colors[4 * i] for i in range(count)]
    assert _alpha(geo, 0) == 1
    assert _alpha(geo, count - 1) == 0


def test_gfx_fx_07_fire_is_added_on_but_smoke_and_rings_are_laid_over() -> None:
    added = {layer: entry[1] for layer, entry in br.LAYERS.items()}
    assert added == {
        "smoke": False,
        "rings": False,
        "fireballs": False,
        "debris": True,
        "embers": True,
    }
    assert set(br.LAYERS) == set(BLAST_LAYERS)
    # Each layer's disc is made when asked for.
    assert all(len(entry[0]().positions) > 0 for entry in br.LAYERS.values())


@pytest.fixture
def babylon(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Babylon stand-ins: the meshes and materials made, and typed arrays for the buffers."""
    made = SimpleNamespace(meshes=[], materials=[], data=[])

    def new_mesh(name: str, _scene: Any) -> Any:
        made.meshes.append(MagicMock(name=name))
        return made.meshes[-1]

    def new_material(name: str, _scene: Any) -> Any:
        made.materials.append(MagicMock(name=name))
        return made.materials[-1]

    stub_babylon(monkeypatch, br)
    monkeypatch.setattr(br, "new_mesh", new_mesh)
    monkeypatch.setattr(br, "new_standard_material", new_material)
    monkeypatch.setattr(br, "vertex_data_of", lambda *args: ("data", *args))
    monkeypatch.setattr(br, "apply_vertex_data", lambda data, mesh: made.data.append((data, mesh)))
    monkeypatch.setattr(br, "babylon_constant", lambda key: key)
    monkeypatch.setattr(br, "color3", lambda r, g, b: (r, g, b))
    monkeypatch.setattr(br, "color3_black", lambda: (0, 0, 0))
    monkeypatch.setattr(br, "_float32_array", FakeTypedArray)
    return made


@pytest.mark.parametrize(("add", "mode"), [(True, "ALPHA_ADD"), (False, "ALPHA_COMBINE")])
def test_gfx_fx_09_a_layer_is_one_unlit_mesh_drawn_in_its_order(
    babylon: SimpleNamespace, add: bool, mode: str
) -> None:
    geo = br.soft(4)
    layer = br.LayerMesh("blast-debris", geo, add, -3.4, 3, "scene")
    mesh = babylon.meshes[0]
    assert layer.mesh is mesh
    assert layer.z == -3.4
    assert babylon.data == [(("data", geo.positions, geo.indices, None, geo.colors), mesh)]
    material = babylon.materials[0]
    assert mesh.material is material
    assert material.emissiveColor == (1, 1, 1)
    assert material.disableLighting is True
    assert material.backFaceCulling is False
    assert material.alphaMode == mode
    assert material.alpha < 1
    assert material.disableDepthWrite is True
    # Laid-over layers take their opacity from the vertex colours.
    assert mesh.hasVertexAlpha is (not add)
    assert mesh.isPickable is False
    assert mesh.alphaIndex == 3
    assert mesh.alwaysSelectAsActiveMesh is True
    mesh.setEnabled.assert_called_once_with(False)


def _spot(x: float, y: float, radius: float, color: list[float], a: float = 1) -> BlastSpot:
    return BlastSpot(x, y, radius, color, a)


def test_gfx_fx_05_a_layer_with_nothing_to_draw_is_hidden(babylon: SimpleNamespace) -> None:
    layer = br.LayerMesh("blast-smoke", br.soft(4), False, -2.8, 0, "scene")
    babylon.meshes[0].reset_mock()
    layer.show([])
    babylon.meshes[0].setEnabled.assert_called_once_with(False)
    babylon.meshes[0].thinInstanceSetBuffer.assert_not_called()


def test_gfx_fx_09_each_spot_is_one_instance_scaled_and_tinted(babylon: SimpleNamespace) -> None:
    layer = br.LayerMesh("blast-fireballs", br.soft(4), False, -3.2, 2, "scene")
    mesh = babylon.meshes[0]
    layer.show([_spot(1, 2, 3, [0.9, 0.5, 0.1], 0.8), _spot(4, 5, 6, [0.1, 0.1, 0.1], 0.5)])
    mesh.setEnabled.assert_called_with(True)
    assert layer.matrices[0:16] == [3, 0, 0, 0, 0, 3, 0, 0, 0, 0, 1, 0, 1, 2, -3.2, 1]
    assert layer.matrices[16:32] == [6, 0, 0, 0, 0, 6, 0, 0, 0, 0, 1, 0, 4, 5, -3.2, 1]
    assert layer.colors[0:8] == [0.9, 0.5, 0.1, 0.8, 0.1, 0.1, 0.1, 0.5]
    # The first spots make buffers for 16 instances.
    assert len(layer.matrices) == 16 * 16
    assert len(layer.colors) == 16 * 4
    assert mesh.thinInstanceSetBuffer.call_args_list == [
        (("matrix", layer.matrices, 16, False),),
        (("color", layer.colors, 4, False),),
    ]
    assert mesh.thinInstanceCount == 2
    mesh.thinInstanceBufferUpdated.assert_not_called()


def test_eng_19_a_layer_reuses_its_buffers_while_they_are_big_enough(
    babylon: SimpleNamespace,
) -> None:
    layer = br.LayerMesh("blast-embers", br.soft(4), True, -3.5, 4, "scene")
    mesh = babylon.meshes[0]
    layer.show([_spot(0, 0, 1, [1, 1, 1])])
    buffers = (layer.matrices, layer.colors)
    mesh.reset_mock()
    layer.show([_spot(7, 8, 2, [1, 0, 0]), _spot(0, 0, 1, [0, 1, 0])])
    assert (layer.matrices, layer.colors) == buffers
    assert layer.matrices[12:14] == [7, 8]
    mesh.thinInstanceSetBuffer.assert_not_called()
    assert mesh.thinInstanceBufferUpdated.call_args_list == [(("matrix",),), (("color",),)]
    assert mesh.thinInstanceCount == 2


def test_eng_19_a_layer_grows_its_buffers_by_powers_of_two(babylon: SimpleNamespace) -> None:
    layer = br.LayerMesh("blast-debris", br.soft(4), True, -3.4, 3, "scene")
    layer.show([_spot(0, 0, 1, [1, 1, 1])])
    layer.show([_spot(i, 0, 1, [1, 1, 1]) for i in range(20)])
    assert len(layer.matrices) == 32 * 16
    assert len(layer.colors) == 32 * 4
    assert babylon.meshes[0].thinInstanceCount == 20


def test_a_layer_disposes_its_mesh_and_its_material(babylon: SimpleNamespace) -> None:
    layer = br.LayerMesh("blast-rings", br.ring(4), False, -3, 1, "scene")
    layer.dispose()
    babylon.meshes[0].dispose.assert_called_once()
    babylon.materials[0].dispose.assert_called_once()


def test_a_layer_without_a_material_disposes_its_mesh(babylon: SimpleNamespace) -> None:
    layer = br.LayerMesh("blast-rings", br.ring(4), False, -3, 1, "scene")
    layer.mesh.material = None
    layer.dispose()
    babylon.meshes[0].dispose.assert_called_once()
    babylon.materials[0].dispose.assert_not_called()


class _Layer:
    """A layer mesh stand-in: what it was made with, the spots of each `show`, and its disposal."""

    made: ClassVar[list[Any]] = []

    def __init__(self, name: str, geo: Any, add: bool, z: float, order: int, scene: Any) -> None:
        self.name = name
        self.geo = geo
        self.add = add
        self.z = z
        self.order = order
        self.scene = scene
        self.shown: list[Any] = []
        self.disposed = False
        _Layer.made.append(self)

    def show(self, spots: list[Any]) -> None:
        self.shown.append(spots)

    def dispose(self) -> None:
        self.disposed = True


class _Particles:
    """The blast particles' stand-in: the blasts emitted, the steps, and the spots it returns."""

    made: ClassVar[list[Any]] = []

    def __init__(self, random: Any) -> None:
        self.random = random
        self.emitted: list[Any] = []
        self.steps: list[float] = []
        self.spots = {layer: [layer + "-spot"] for layer in BLAST_LAYERS}
        _Particles.made.append(self)

    def emit(self, blast: Any) -> None:
        self.emitted.append(blast)

    def step(self, dt: float) -> dict[str, list[Any]]:
        self.steps.append(dt)
        return self.spots


@pytest.fixture
def renderer(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Return the blast renderer over layer and particle stand-ins."""
    _Layer.made = []
    _Particles.made = []
    monkeypatch.setattr(br, "LayerMesh", _Layer)
    monkeypatch.setattr(br, "BlastParticles", _Particles)
    handle = br.create_blast_renderer("scene")
    return SimpleNamespace(handle=handle, layers=_Layer.made, particles=_Particles.made[0])


def test_gfx_fx_09_the_renderer_makes_one_layer_mesh_per_blast_layer_in_order(
    renderer: SimpleNamespace,
) -> None:
    layers = renderer.layers
    assert [layer.name for layer in layers] == ["blast-" + layer for layer in BLAST_LAYERS]
    assert [layer.order for layer in layers] == list(range(len(BLAST_LAYERS)))
    assert [layer.z for layer in layers] == [br.LAYERS[layer][2] for layer in BLAST_LAYERS]
    assert [layer.add for layer in layers] == [br.LAYERS[layer][1] for layer in BLAST_LAYERS]
    assert all(layer.scene == "scene" for layer in layers)
    assert isinstance(renderer.handle, br.BlastRendererHandle)


def test_the_blasts_are_seeded_from_the_look(renderer: SimpleNamespace) -> None:
    # The particles' random numbers come from the look's seed: the same blasts every run.
    first = [renderer.particles.random() for _ in range(3)]
    br.create_blast_renderer("scene")
    assert [_Particles.made[1].random() for _ in range(3)] == first


def test_gfx_fx_05_each_frame_starts_the_new_blasts_and_draws_every_layer(
    renderer: SimpleNamespace,
) -> None:
    blasts = [SimpleNamespace(kind="enemy"), SimpleNamespace(kind="missile")]
    renderer.handle.sync(blasts, 0.02)
    assert renderer.particles.emitted == blasts
    assert renderer.particles.steps == [0.02]
    for layer, mesh in zip(BLAST_LAYERS, renderer.layers, strict=True):
        assert mesh.shown == [[layer + "-spot"]]


def test_gfx_fx_05_dispose_releases_every_layer(renderer: SimpleNamespace) -> None:
    renderer.handle.dispose()
    assert all(layer.disposed for layer in renderer.layers)
