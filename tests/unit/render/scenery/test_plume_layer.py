"""Unit tests of `src/render/scenery/plume_layer.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, patch_babylon

from config.plumes import PLUME_KINDS, PlumeKind
from core.scenery.atmosphere import Ambient, Atmosphere, Fog, Sky, Sun
from render.scenery import plume_layer
from render.scenery.plume_layer import (
    PLUME_ALPHA_INDEX,
    PLUME_LIGHT,
    PlumeFog,
    PlumeFrame,
    build_plume_meshes,
    plume_geometry,
    plume_light,
)
from render.scenery.scenery_look import PropPlume


def _kind(puffs: int = 3) -> PlumeKind:
    return PlumeKind(puffs, 4, 20, 2, (1, 2), (0.3, 0.3, 0.3), 0.5, 0.0)


def _atmosphere(
    sky: tuple[float, float, float], intensity: float, sun_color: Any, sun_intensity: float
) -> Atmosphere:
    return Atmosphere(
        Sun(45, 0, sun_color, sun_intensity, 0.5),
        Sky((0, 0, 0), [], 1),
        Ambient(sky, (0, 0, 0), intensity),
        Fog(10, 100),
        [],
        0.0,
        SimpleNamespace(kind="snow", strength=0),
        0.0,
        0.0,
    )


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, plume_layer)
    monkeypatch.setattr(plume_layer, "new_mesh", _new_mesh)
    monkeypatch.setattr(
        plume_layer, "vertex_data_of", lambda positions, indices: (positions, indices)
    )
    monkeypatch.setattr(plume_layer, "apply_vertex_data", lambda data, mesh: None)


def _new_mesh(label: str, scene: FakeScene) -> FakeNode:
    node = scene.add_node(label, is_mesh=True)
    node.vertexData = {}
    node.setVerticesData = lambda name, values, updatable, stride: node.vertexData.__setitem__(
        name, values
    )
    return node


def test_a_plume_frame_and_its_fog_keep_what_they_are_given() -> None:
    fog = PlumeFog((0.1, 0.2, 0.3), 5, 50)
    frame = PlumeFrame(3.0, "camera", "right", "up", (0.4, 0.5, 0.6), fog)
    assert (frame.time, frame.camera_position, frame.right, frame.up) == (
        3.0,
        "camera",
        "right",
        "up",
    )
    assert frame.light == (0.4, 0.5, 0.6)
    assert frame.fog is fog
    assert (fog.color, fog.start, fog.end) == ((0.1, 0.2, 0.3), 5, 50)


def test_each_column_puffs_as_many_quads_as_its_kind_has() -> None:
    plumes = [PropPlume((0, 0, 0), "smoke"), PropPlume((5, 0, 0), "smoke")]
    geometry = plume_geometry(plumes, _kind(puffs=3))
    assert len(geometry.positions) == 2 * 3 * 4 * 3
    assert len(geometry.puffs) == 2 * 3 * 4 * 4
    assert len(geometry.scales) == 2 * 3 * 4
    assert len(geometry.indices) == 2 * 3 * 6


def test_the_quads_are_flat_around_the_foot_of_each_column() -> None:
    geometry = plume_geometry([PropPlume((0, 0, 0), "smoke")], _kind(puffs=1))
    xs = geometry.positions[0::3]
    ys = geometry.positions[1::3]
    zs = geometry.positions[2::3]
    assert set(zs) == {0}
    assert sorted(xs[:4]) == [-0.5, -0.5, 0.5, 0.5]
    assert sorted(ys[:4]) == [-0.5, -0.5, 0.5, 0.5]


def test_each_vertex_carries_its_column_start_and_its_puff_phase() -> None:
    geometry = plume_geometry([PropPlume((1.0, 2.0, 3.0), "smoke")], _kind(puffs=2))
    for vertex in range(8):
        assert geometry.puffs[vertex * 4 : vertex * 4 + 3] == [1.0, 2.0, 3.0]
    assert geometry.puffs[3] == pytest.approx(0)
    assert geometry.puffs[4 * 4 + 3] == pytest.approx(0.5)


def test_the_puffs_of_one_column_are_spread_evenly_up_it() -> None:
    geometry = plume_geometry([PropPlume((0, 0, 0), "smoke")], _kind(puffs=3))
    phases = [geometry.puffs[v * 4 + 3] for v in range(0, 12, 4)]
    assert phases == [pytest.approx(0), pytest.approx(1 / 3), pytest.approx(2 / 3)]


def test_neighbouring_columns_start_out_of_step() -> None:
    geometry = plume_geometry(
        [PropPlume((0, 0, 0), "smoke"), PropPlume((5, 0, 0), "smoke")], _kind(puffs=3)
    )
    first_of_each = [geometry.puffs[3], geometry.puffs[12 * 4 + 3]]
    assert first_of_each[0] != pytest.approx(first_of_each[1])


def test_a_column_without_a_scale_is_drawn_at_scale_one_and_one_with_a_scale_at_that_scale() -> (
    None
):
    geometry = plume_geometry(
        [PropPlume((0, 0, 0), "smoke"), PropPlume((0, 0, 0), "smoke", 2.5)], _kind(puffs=1)
    )
    assert geometry.scales[0] == 1
    assert geometry.scales[4] == 2.5


def test_a_plume_light_takes_the_ambient_light_and_some_of_the_sun() -> None:
    atmosphere = _atmosphere((0.5, 0.0, 0.2), 1.0, (1, 1, 1), 1.0)
    red, green, blue = plume_light(atmosphere)
    assert red == pytest.approx(0.5 + PLUME_LIGHT.sun)
    assert green == pytest.approx(PLUME_LIGHT.sun)
    assert blue == pytest.approx(0.2 + PLUME_LIGHT.sun)


def test_a_plume_light_is_capped_at_its_most() -> None:
    atmosphere = _atmosphere((5.0, 5.0, 5.0), 1.0, (1, 1, 1), 1.0)
    assert plume_light(atmosphere) == (PLUME_LIGHT.most,) * 3


def test_a_plume_light_at_night_is_only_the_ambient_light() -> None:
    atmosphere = _atmosphere((0.3, 0.3, 0.3), 0.5, (1, 1, 1), 0.0)
    assert plume_light(atmosphere) == pytest.approx((0.15, 0.15, 0.15))


def test_a_mesh_is_made_for_each_plume_kind_a_prop_has() -> None:
    plumes = [
        PropPlume((0, 0, 0), "smoke"),
        PropPlume((1, 0, 0), "steam"),
        PropPlume((2, 0, 0), "smoke"),
    ]
    meshes = build_plume_meshes(FakeScene(), "chimney", plumes, lambda kind: "mat-" + kind)
    assert [mesh.name for mesh in meshes] == ["chimney-plume-smoke", "chimney-plume-steam"]
    assert [mesh.material for mesh in meshes] == ["mat-smoke", "mat-steam"]


def test_a_plume_mesh_is_always_selected_see_through_and_starts_hidden() -> None:
    meshes = build_plume_meshes(
        FakeScene(), "chimney", [PropPlume((0, 0, 0), "smoke")], lambda kind: "m"
    )
    mesh = meshes[0]
    assert mesh.alwaysSelectAsActiveMesh is True
    assert mesh.isPickable is False
    assert mesh.alphaIndex == PLUME_ALPHA_INDEX
    assert mesh.enabled is False


def test_a_plume_mesh_holds_the_puffs_of_its_kind() -> None:
    plumes = [PropPlume((0, 0, 0), "smoke")]
    mesh = build_plume_meshes(FakeScene(), "chimney", plumes, lambda kind: "m")[0]
    assert len(mesh.vertexData["puff"]) == PLUME_KINDS["smoke"].puffs * 4 * 4
    assert len(mesh.vertexData["puffScale"]) == PLUME_KINDS["smoke"].puffs * 4


def test_a_plume_of_an_unknown_kind_or_without_a_material_makes_no_mesh() -> None:
    plumes = [PropPlume((0, 0, 0), "lava-fume"), PropPlume((0, 0, 0), "smoke")]
    meshes = build_plume_meshes(
        FakeScene(), "p", plumes, lambda kind: None if kind == "smoke" else "m"
    )
    assert meshes == []
    meshes = build_plume_meshes(FakeScene(), "p", plumes, lambda kind: "m")
    assert [mesh.name for mesh in meshes] == ["p-plume-smoke"]


def test_a_given_table_of_kinds_is_used_instead_of_the_engine_kinds() -> None:
    table = {"ember": _kind()}
    meshes = build_plume_meshes(
        FakeScene(), "p", [PropPlume((0, 0, 0), "ember")], lambda kind: "m", table
    )
    assert [mesh.name for mesh in meshes] == ["p-plume-ember"]


def test_a_prop_with_no_plumes_makes_no_mesh() -> None:
    assert build_plume_meshes(FakeScene(), "p", [], lambda kind: "m") == []
