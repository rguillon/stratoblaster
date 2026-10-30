"""Unit tests of `src/render/scenery/road_field.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeScene, patch_babylon
from helpers.render_looks import make_look

from core.scenery.road_types import Road, RoadPoint
from core.scenery.scenery_level import TileRules
from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery import road_field
from render.scenery.road_field import RoadField, RoadLayers, _opaque_of, _split_roads
from render.scenery.tile_road_geometry import TileRoadLook

SLOTS: dict[tuple[int, str], Any] = {}


class FakeMaterial:
    """A Babylon material: a name, a clone, and the depth fields the road code sets."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.disableDepthWrite = True  # noqa: N815 (Babylon's name)
        self.zOffset = 0.0  # noqa: N815
        self.diffuseTexture: Any = None  # noqa: N815

    def clone(self, name: str) -> "FakeMaterial":
        return FakeMaterial(name)


class FakeTexture:
    def __init__(self) -> None:
        self.anisotropicFilteringLevel = 1  # noqa: N815


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    """The Babylon calls of the road meshes and textures, as plain Python, and the slots that
    keep the split of a list of roads (JavaScript properties in the browser)."""
    patch_babylon(monkeypatch, road_field)
    SLOTS.clear()
    monkeypatch.setattr(road_field, "_slot_get", lambda o, s: SLOTS.get((id(o), s)))
    monkeypatch.setattr(road_field, "_slot_set", lambda o, s, v: SLOTS.__setitem__((id(o), s), v))
    monkeypatch.setattr(road_field, "compute_normals", lambda p, i: [0.0] * len(p))
    monkeypatch.setattr(road_field, "new_vertex_data", SimpleNamespace)
    monkeypatch.setattr(road_field, "apply_vertex_data", lambda data, mesh: None)
    monkeypatch.setattr(road_field, "texture_trilinear_sampling_mode", lambda: 0)
    monkeypatch.setattr(road_field, "raw_rgba_texture", lambda *a: FakeTexture())
    monkeypatch.setattr(road_field, "update_raw_texture", lambda t, p: None)


def _triangle() -> ColoredGeometry:
    geo = ColoredGeometry()
    geo.positions = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    geo.indices = [0, 1, 2]
    geo.colors = [1.0, 1.0, 1.0, 1.0] * 3
    return geo


def _road(index: int, kind: str, z0: float = 0) -> Road:
    points = [RoadPoint(0, z0 + i * 10, 4) for i in range(3)]
    return Road(index, kind, 4, 1, points)


def test_a_chunk_gets_one_mesh_named_for_it_with_its_draw_order_and_material() -> None:
    scene = FakeScene()
    material = FakeMaterial("road")
    field = RoadField(scene, material, "roads", -1)
    field.set_chunk(3, _triangle())
    assert field.count == 1
    mesh = field.mesh(3)
    assert mesh.name == "roads-3"
    assert mesh.alphaIndex == -1
    assert mesh.hasVertexAlpha is True
    assert mesh.material is material
    assert mesh.isPickable is False


def test_an_opaque_field_is_drawn_without_fading_with_its_vertex_alpha() -> None:
    field = RoadField(FakeScene(), FakeMaterial("m"), "streets", 0, see_through=False)
    field.set_chunk(0, _triangle())
    assert field.mesh(0).hasVertexAlpha is False


def test_a_chunk_without_triangles_has_no_mesh() -> None:
    field = RoadField(FakeScene(), FakeMaterial("m"), "roads", -1)
    field.set_chunk(0, ColoredGeometry())
    assert field.count == 0
    assert field.mesh(0) is None


def test_setting_a_chunk_again_replaces_its_mesh() -> None:
    field = RoadField(FakeScene(), FakeMaterial("m"), "roads", -1)
    field.set_chunk(0, _triangle())
    first = field.mesh(0)
    field.set_chunk(0, _triangle())
    assert field.count == 1
    assert first.disposed
    assert field.mesh(0) is not first


def test_removing_a_chunk_disposes_its_mesh_and_clear_removes_them_all() -> None:
    field = RoadField(FakeScene(), FakeMaterial("m"), "roads", -1)
    field.set_chunk(0, _triangle())
    field.set_chunk(1, _triangle())
    kept = field.mesh(1)
    field.remove_chunk(0)
    assert field.mesh(0) is None
    assert field.count == 1
    field.clear()
    assert field.count == 0
    assert kept.disposed


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
    flat = SimpleNamespace(height=lambda x, z: 0.0)
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    layers.set_chunk(0, [_road(1, "street")], flat, (0, 100), look)
    assert layers.streets_of(0) is not None
    layers.set_chunk(1, [_road(2, "street"), _road(3, "main")], flat, (0, 100), look)
    assert layers.streets_of(1) is None


def test_the_count_of_the_layers_is_the_chunks_with_ribbons_and_clear_empties_them() -> None:
    look = make_look().roads
    flat = SimpleNamespace(height=lambda x, z: 0.0)
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    roads = [_road(1, "main"), _road(2, "cross")]
    layers.set_chunk(0, roads, flat, (0, 100), look)
    layers.set_chunk(1, roads, flat, (0, 100), look)
    assert layers.count == 2
    layers.remove_chunk(0)
    assert layers.count == 1
    layers.clear()
    assert layers.count == 0


def test_the_street_surfaces_of_a_tile_chunk_are_shown_with_the_road_atlas() -> None:
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    layers.show_tile_grid()
    chunk = SimpleNamespace(
        atlas=[1, 2, 3],
        surfaces=_triangle(),
        layered=_triangle(),
        grid=_triangle(),
    )
    layers.set_tile_chunk(4, chunk)
    assert layers._atlas_texture.anisotropicFilteringLevel == 8
    assert layers._surface_material.diffuseTexture is layers._atlas_texture
    assert layers.streets_of(4) is not None
    assert layers._grid.mesh(4) is not None


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
    flat = SimpleNamespace(height=lambda x, z: 0.0)
    layers = RoadLayers(FakeScene(), FakeMaterial("road"))
    roads = [_road(1, "street"), _road(2, "cross"), _road(3, "main")]
    layers.set_chunk(0, roads, flat, (0, 100), look, TileRules(10, 2))
    assert layers.streets_of(0) is None
    assert layers._paths.mesh(0) is not None
    assert layers._roads.mesh(0) is not None
