# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/road_field.py` (GFX-ROAD-06, GFX-ROAD-22)."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeScene, patch_babylon
from helpers.render_looks import make_look

from core.scenery.road_types import Road, RoadPoint
from core.scenery.scenery_level import TileRules
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery import road_field
from render.scenery.road_field import (
    RoadField,
    RoadLayers,
    _opaque_of,
    _slot_get,
    _slot_set,
    _split_roads,
)
from render.scenery.road_geometry import RoadLook
from render.scenery.tile_road_geometry import TileRoadLook

SLOTS: dict[tuple[int, str], Any] = {}


class FakeMaterial:
    """A Babylon material: a name, a clone, and the depth fields the road code sets."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.disableDepthWrite = True
        self.zOffset = 0.0
        self.diffuseTexture: Any = None

    def clone(self, name: str) -> "FakeMaterial":
        return FakeMaterial(name)


class FakeTexture:
    def __init__(self) -> None:
        self.anisotropicFilteringLevel = 1


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the Babylon calls of the road meshes and textures with plain Python.

    The slots keep the split of a list of roads (JavaScript properties in the browser).
    """
    patch_babylon(monkeypatch, road_field)
    SLOTS.clear()
    monkeypatch.setattr(road_field, "_slot_get", lambda o, s: SLOTS.get((id(o), s)))
    monkeypatch.setattr(road_field, "_slot_set", lambda o, s, v: SLOTS.__setitem__((id(o), s), v))
    monkeypatch.setattr(road_field, "compute_normals", lambda p, _i: [0.0] * len(p))
    monkeypatch.setattr(road_field, "new_vertex_data", SimpleNamespace)
    monkeypatch.setattr(road_field, "apply_vertex_data", lambda _data, _mesh: None)
    monkeypatch.setattr(road_field, "texture_trilinear_sampling_mode", lambda: 0)
    monkeypatch.setattr(road_field, "raw_rgba_texture", lambda *_a: FakeTexture())
    monkeypatch.setattr(road_field, "update_raw_texture", lambda _t, _p: None)


def _triangle() -> ColoredGeometry:
    geo = ColoredGeometry()
    geo.positions = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    geo.indices = [0, 1, 2]
    geo.colors = [1.0, 1.0, 1.0, 1.0] * 3
    return geo


def _road(index: int, kind: str, z0: float = 0) -> Road:
    points = [RoadPoint(0, z0 + i * 10, 4) for i in range(3)]
    return Road(index, kind, 4, 1, points)


def _mesh(field: RoadField, index: int) -> Any:
    """Return the mesh of chunk `index` of `field`, if it has one."""
    i = field._position(index)
    return field._meshes[i] if i >= 0 else None


def test_a_chunk_gets_one_mesh_named_for_it_with_its_draw_order_and_material() -> None:
    scene = FakeScene()
    material = FakeMaterial("road")
    field = RoadField(scene, material, "roads", -1)
    field.set_chunk(3, _triangle())
    assert field.count == 1
    mesh = _mesh(field, 3)
    assert mesh.name == "roads-3"
    assert mesh.alphaIndex == -1
    assert mesh.hasVertexAlpha is True
    assert mesh.material is material
    assert mesh.isPickable is False


def test_an_opaque_field_is_drawn_without_fading_with_its_vertex_alpha() -> None:
    field = RoadField(FakeScene(), FakeMaterial("m"), "streets", 0, see_through=False)
    field.set_chunk(0, _triangle())
    assert _mesh(field, 0).hasVertexAlpha is False


def test_a_chunk_without_triangles_has_no_mesh() -> None:
    field = RoadField(FakeScene(), FakeMaterial("m"), "roads", -1)
    field.set_chunk(0, ColoredGeometry())
    assert field.count == 0
    assert _mesh(field, 0) is None


def test_setting_a_chunk_again_replaces_its_mesh() -> None:
    field = RoadField(FakeScene(), FakeMaterial("m"), "roads", -1)
    field.set_chunk(0, _triangle())
    first = _mesh(field, 0)
    field.set_chunk(0, _triangle())
    assert field.count == 1
    assert first.disposed
    assert _mesh(field, 0) is not first


def test_removing_a_chunk_disposes_its_mesh_and_keeps_the_others() -> None:
    field = RoadField(FakeScene(), FakeMaterial("m"), "roads", -1)
    field.set_chunk(0, _triangle())
    field.set_chunk(1, _triangle())
    removed = _mesh(field, 0)
    kept = _mesh(field, 1)
    field.remove_chunk(0)
    assert _mesh(field, 0) is None
    assert removed.disposed
    assert field.count == 1
    assert _mesh(field, 1) is kept
    assert not kept.disposed


def test_paths_are_split_from_the_other_roads_and_a_list_of_streets_is_known() -> None:
    roads = [_road(1, "street"), _road(2, "cross"), _road(3, "main")]
    split = _split_roads(roads)
    assert [r.index for r in split.paths] == [2]
    assert [r.index for r in split.roads] == [1, 3]
    assert split.streets_only is False


def test_a_list_of_only_streets_is_streets_only() -> None:
    assert _split_roads([_road(1, "street"), _road(2, "street")]).streets_only is True


def test_the_split_of_a_list_is_made_once_and_kept_with_it() -> None:
    roads = [_road(1, "street")]
    assert _split_roads(roads) is _split_roads(roads)


def test_the_opaque_road_material_is_a_clone_written_in_depth_with_the_street_offset() -> None:
    base = FakeMaterial("road")
    opaque = _opaque_of(base)
    assert opaque is not base
    assert opaque.name == "road-opaque"
    assert opaque.disableDepthWrite is False
    assert opaque.zOffset == -1


def test_the_middles_of_all_street_chunks_are_drawn_apart_and_mixed_roads_are_not() -> None:
    look = make_look().roads
    flat = SimpleNamespace(height=lambda _x, _z: 0.0)
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    layers.set_chunk(0, [_road(1, "street")], flat, (0, 100), look)
    assert _mesh(layers._streets, 0) is not None
    layers.set_chunk(1, [_road(2, "street"), _road(3, "main")], flat, (0, 100), look)
    assert _mesh(layers._streets, 1) is None


def test_the_count_of_the_layers_is_the_chunks_with_ribbons() -> None:
    look = make_look().roads
    flat = SimpleNamespace(height=lambda _x, _z: 0.0)
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    roads = [_road(1, "main"), _road(2, "cross")]
    layers.set_chunk(0, roads, flat, (0, 100), look)
    layers.set_chunk(1, roads, flat, (0, 100), look)
    assert layers.count == 2
    layers.remove_chunk(0)
    assert layers.count == 1


def test_the_street_surfaces_of_a_tile_chunk_are_shown_with_the_road_atlas() -> None:
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    layers.show_tile_grid()
    chunk = SimpleNamespace(
        atlas=[1, 2, 3],
        atlas_version=1,
        surfaces=_triangle(),
        layered=_triangle(),
        grid=_triangle(),
    )
    layers.set_tile_chunk(4, chunk)
    assert layers._atlas_texture.anisotropicFilteringLevel == 8
    assert layers._surface_material.diffuseTexture is layers._atlas_texture
    assert _mesh(layers._streets, 4) is not None
    assert _mesh(layers._grid, 4) is not None


def _tile_chunk(atlas: Any, version: int) -> Any:
    return SimpleNamespace(
        atlas=atlas, atlas_version=version, surfaces=_triangle(), layered=_triangle(), grid=None
    )


def test_d217_each_version_of_the_road_atlas_is_uploaded_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GFX-ROAD-21."""
    uploads: list[Any] = []
    monkeypatch.setattr(road_field, "update_raw_texture", lambda _t, p: uploads.append(p))
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    layers.set_tile_chunk(0, _tile_chunk([1], 1))
    texture = layers._atlas_texture
    # Every chunk comes with the latest atlas: the same version is not uploaded again.
    layers.set_tile_chunk(1, _tile_chunk([1], 1))
    layers.set_tile_chunk(2, _tile_chunk(None, 0))
    assert uploads == []
    layers.set_tile_chunk(3, _tile_chunk([2], 2))
    assert uploads == [[2]]
    assert layers._atlas_texture is texture


def test_the_tile_grid_is_drawn_over_the_ground_with_its_own_material_offset() -> None:
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    layers.show_tile_grid()
    grid_material = layers._grid._material
    assert grid_material.name == "tile-grid"
    assert grid_material.zOffset == -3
    assert grid_material.disableDepthWrite is False


def test_on_a_tile_path_the_streets_are_not_made_in_the_road_chunk() -> None:
    look = make_look().roads
    look.tiles = TileRoadLook(
        (0.5, 0.5, 0.5),
        (1.0, 1.0, 1.0),
        (0.0, 0.0, 0.0),
        0.5,
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        0.3,
        0.1,
    )
    flat = SimpleNamespace(height=lambda _x, _z: 0.0)
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    roads = [_road(1, "street"), _road(2, "cross"), _road(3, "main")]
    layers.set_chunk(0, roads, flat, (0, 100), look, TileRules(10, 2))
    assert _mesh(layers._streets, 0) is None
    assert _mesh(layers._paths, 0) is not None
    assert _mesh(layers._roads, 0) is not None


def test_the_slots_are_javascript_only_and_hold_nothing_under_cpython() -> None:
    """JavaScript-only: the browser keeps the value on the list; CPython runs the placeholder."""
    roads: list[Road] = []
    assert _slot_set(roads, "render_road_split", "kept") is None
    assert _slot_get(roads, "render_road_split") is None


def test_a_chunk_with_texture_coordinates_passes_them_to_its_mesh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    applied: list[Any] = []
    monkeypatch.setattr(road_field, "apply_vertex_data", lambda data, _mesh: applied.append(data))
    textured = _triangle()
    textured.uvs = [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]  # type: ignore[attr-defined]
    field = RoadField(FakeScene(), FakeMaterial("m"), "street-surfaces", 0, False)
    field.set_chunk(0, textured)
    field.set_chunk(1, _triangle())
    assert applied[0].uvs == textured.uvs
    assert not hasattr(applied[1], "uvs")


def _tile_look() -> RoadLook:
    look = make_look().roads
    look.tiles = TileRoadLook(
        (0.5, 0.5, 0.5),
        (1.0, 1.0, 1.0),
        (0.0, 0.0, 0.0),
        0.5,
        (1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        0.3,
        0.1,
    )
    return look


def test_on_a_tile_path_the_winding_roads_of_a_list_are_picked_once_and_kept_with_it() -> None:
    flat = SimpleNamespace(height=lambda _x, _z: 0.0)
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    roads = [_road(1, "street"), _road(2, "main")]
    look = _tile_look()
    layers.set_chunk(0, roads, flat, (0, 100), look, TileRules(10, 2))
    kept = SLOTS[(id(roads), "render_road_winding")]
    assert [r.index for r in kept] == [2]
    layers.set_chunk(1, roads, flat, (0, 100), look, TileRules(10, 2))
    assert SLOTS[(id(roads), "render_road_winding")] is kept
    assert _mesh(layers._roads, 1) is not None


def test_the_tile_grid_is_made_once() -> None:
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    layers.show_tile_grid()
    grid = layers._grid
    layers.show_tile_grid()
    assert layers._grid is grid


class _UnclonableMaterial(FakeMaterial):
    """A material whose clone gives nothing (as Babylon may)."""

    def clone(self, _name: str) -> Any:
        return None


def test_the_tile_grid_takes_the_road_material_itself_when_it_cannot_be_cloned() -> None:
    material = _UnclonableMaterial("road")
    layers = RoadLayers(FakeScene(), material)
    layers.show_tile_grid()
    assert layers._grid._material is material
    assert material.zOffset == -3
    assert material.disableDepthWrite is False


def test_the_tile_grid_goes_with_its_chunk() -> None:
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    layers.show_tile_grid()
    for index in (0, 1):
        layers.set_tile_chunk(
            index,
            SimpleNamespace(
                atlas=None,
                atlas_version=0,
                surfaces=_triangle(),
                layered=_triangle(),
                grid=_triangle(),
            ),
        )
    grid = layers._grid
    assert grid.count == 2
    layers.remove_chunk(0)
    assert _mesh(grid, 0) is None
    assert grid.count == 1
    assert _mesh(layers._streets, 0) is None
    assert _mesh(layers._streets, 1) is not None
