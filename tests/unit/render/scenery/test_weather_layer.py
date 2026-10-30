"""Unit tests of `src/render/scenery/weather_layer.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, FakeVector, patch_babylon
from helpers.sample_level import sample_atmosphere

from config.weather import WEATHER_KINDS
from core.scenery.atmosphere import Weather
from render.scenery import weather_layer
from render.scenery.weather_layer import (
    QUAD_INDICES,
    WEATHER_ALPHA_INDEX,
    WeatherFrame,
    WeatherLayer,
    WeatherView,
    _build_particles,
    _draw_first,
)

# What the patched Babylon mesh calls received, in order.
_VERTEX_DATA: list[Any] = []
_SUB_MESHES: list[Any] = []


class _Material:
    """A particle material: the frames it was driven with."""

    def __init__(self, kind: Any) -> None:
        self.kind = kind
        self.material = "particles-of-" + str(kind.color)
        self.frames: list[WeatherFrame] = []

    def set(self, frame: WeatherFrame) -> None:
        self.frames.append(frame)


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    _VERTEX_DATA.clear()
    _SUB_MESHES.clear()
    patch_babylon(monkeypatch, weather_layer)
    monkeypatch.setattr(weather_layer, "new_mesh", _new_mesh)
    monkeypatch.setattr(weather_layer, "vertex_data_of", _vertex_data_of)
    monkeypatch.setattr(weather_layer, "apply_vertex_data", _apply_vertex_data)
    monkeypatch.setattr(
        weather_layer, "babylon_class", lambda name: SimpleNamespace(AddToMesh=_add_to_mesh)
    )


def _new_mesh(label: str, scene: FakeScene) -> FakeNode:
    node = scene.add_node(label, is_mesh=True)
    node.subMeshes = []
    node.flakes = []
    node.setVerticesData = lambda name, values, updatable, stride: _set_vertices(node, name, values)
    node.releaseSubMeshes = node.subMeshes.clear
    node.getTotalVertices = lambda: node.vertexCount
    node.vertexCount = 0
    return node


def _set_vertices(node: FakeNode, name: str, values: list[float]) -> None:
    if name == "flake":
        node.flakes = list(values)


def _vertex_data_of(positions: list[float], indices: list[int]) -> SimpleNamespace:
    data = SimpleNamespace(positions=list(positions), indices=list(indices))
    _VERTEX_DATA.append(data)
    return data


def _apply_vertex_data(data: SimpleNamespace, mesh: FakeNode) -> None:
    mesh.vertexCount = len(data.positions) // 3
    # Babylon gives a mesh with indices one sub-mesh over all of them.
    mesh.subMeshes = [SimpleNamespace(indexCount=len(data.indices))]


def _add_to_mesh(
    index: int, _end: int, _vertices: int, start: int, count: int, mesh: FakeNode
) -> None:
    _SUB_MESHES.append((start, count))
    mesh.subMeshes = [SimpleNamespace(indexCount=count)]


def _material_factory(scene: Any, kind: Any) -> _Material:
    return _Material(kind)


def _layer(kinds: Any = WEATHER_KINDS) -> WeatherLayer:
    return WeatherLayer(FakeScene(), _material_factory, kinds)


def _atmosphere(weather: Weather | None = None, second: Weather | None = None) -> Any:
    atmosphere = sample_atmosphere()
    atmosphere.weather = weather or Weather("snow", 0)
    atmosphere.second_weather = second
    return atmosphere


def _view(time: float = 1.0, start: float = -40.0) -> WeatherView:
    return WeatherView(time, FakeVector(0, 5, 0), "right", "up", start)


def _layer_of(layer: WeatherLayer, kind: str) -> Any:
    return layer._layers[kind]


def test_the_particle_constants_are_four_corners_of_two_triangles_and_the_weather_draw_order() -> (
    None
):
    assert QUAD_INDICES == 6
    assert WEATHER_ALPHA_INDEX == 4


def test_a_weather_kind_is_one_mesh_of_its_max_particles_quads() -> None:
    kind = WEATHER_KINDS["snow"]
    mesh = _build_particles(FakeScene(), "snow", kind, "material")
    data = _VERTEX_DATA[-1]
    assert len(data.positions) == kind.max_particles * 4 * 3
    assert len(data.indices) == kind.max_particles * QUAD_INDICES
    assert mesh.material == "material"


def test_the_particles_are_drawn_after_the_clouds_and_placed_by_the_material() -> None:
    mesh = _build_particles(FakeScene(), "rain", WEATHER_KINDS["rain"], "material")
    assert mesh.renderingGroupId == 1
    assert mesh.alphaIndex == WEATHER_ALPHA_INDEX
    assert mesh.alwaysSelectAsActiveMesh is True
    assert mesh.isPickable is False
    assert mesh.enabled is False


def test_each_particle_has_four_random_values_per_corner_fixed_by_the_kind() -> None:
    kind = WEATHER_KINDS["snow"]
    first = _build_particles(FakeScene(), "snow", kind, "m").flakes
    second = _build_particles(FakeScene(), "snow", kind, "m").flakes
    assert len(first) == kind.max_particles * 4 * 4
    assert first == second
    assert all(0 <= value < 1 for value in first)


def test_a_weather_draws_as_many_particles_as_its_strength_asks() -> None:
    layer = _layer()
    layer.update(_atmosphere(Weather("snow", 0.5)), _view())
    assert layer.drawn == 750
    assert _layer_of(layer, "snow").mesh.enabled is True


def test_a_full_strength_weather_draws_its_kind_most() -> None:
    layer = _layer()
    layer.update(_atmosphere(Weather("snow", 1)), _view())
    assert layer.drawn == WEATHER_KINDS["snow"].max_particles


def test_no_strength_draws_no_particles_and_hides_the_mesh() -> None:
    layer = _layer()
    layer.update(_atmosphere(Weather("snow", 1)), _view())
    layer.update(_atmosphere(Weather("snow", 0)), _view())
    assert layer.drawn == 0
    assert _layer_of(layer, "snow").mesh.enabled is False


def test_a_kind_that_is_no_longer_the_weather_is_hidden() -> None:
    layer = _layer()
    layer.update(_atmosphere(Weather("snow", 1)), _view())
    layer.update(_atmosphere(Weather("rain", 1)), _view())
    assert _layer_of(layer, "snow").mesh.enabled is False
    assert _layer_of(layer, "rain").mesh.enabled is True


def test_an_unknown_weather_kind_draws_nothing() -> None:
    layer = _layer()
    layer.update(_atmosphere(Weather("hail", 1)), _view())
    assert layer.drawn == 0
    assert layer._layers == {}


def test_the_second_weather_of_the_atmosphere_is_drawn_too() -> None:
    layer = _layer()
    layer.update(_atmosphere(Weather("snow", 1), Weather("ash", 0.5)), _view())
    assert layer.drawn == WEATHER_KINDS["snow"].max_particles + 750
    assert _layer_of(layer, "ash").mesh.enabled is True


def test_the_material_is_driven_with_the_frame_of_the_view_and_the_fog() -> None:
    layer = _layer()
    atmosphere = _atmosphere(Weather("rain", 0.6))
    view = _view(time=4.0, start=-90.0)
    layer.update(atmosphere, view)
    frame = _layer_of(layer, "rain").material.frames[-1]
    assert frame.time == 4.0
    assert frame.strength == pytest.approx(0.6)
    assert frame.camera_position is view.camera_position
    assert (frame.right, frame.up, frame.start) == ("right", "up", -90.0)
    assert frame.fog.color == atmosphere.sky.haze
    assert (frame.fog.start, frame.fog.end) == (atmosphere.fog.start, atmosphere.fog.end)


def test_each_kind_has_one_material_and_one_mesh_however_many_frames() -> None:
    made: list[Any] = []

    def factory(scene: Any, kind: Any) -> _Material:
        material = _Material(kind)
        made.append(material)
        return material

    layer = WeatherLayer(FakeScene(), factory)
    layer.update(_atmosphere(Weather("snow", 1)), _view())
    layer.update(_atmosphere(Weather("snow", 0.4)), _view())
    assert len(made) == 1
    assert len(layer._layers) == 1
    assert len(made[0].frames) == 2


def test_draw_first_keeps_a_sub_mesh_already_drawing_that_many_particles() -> None:
    mesh = FakeNode()
    mesh.subMeshes = [SimpleNamespace(indexCount=12)]
    _draw_first(mesh, 2)
    assert _SUB_MESHES == []


def test_draw_first_replaces_the_sub_mesh_with_one_over_the_first_particles() -> None:
    mesh = FakeNode()
    mesh.subMeshes = [SimpleNamespace(indexCount=600)]
    mesh.getTotalVertices = lambda: 400
    mesh.releaseSubMeshes = mesh.subMeshes.clear
    _draw_first(mesh, 2)
    assert _SUB_MESHES == [(0, 12)]
    assert mesh.subMeshes[0].indexCount == 12
