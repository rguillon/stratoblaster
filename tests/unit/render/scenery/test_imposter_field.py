# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/imposter_field.py`: the imposters in view (D-211, D-212).

The quad meshes are fakes that record their vertex data and their thin-instance uploads.
"""

import math
from typing import Any

import pytest
from fixtures.sample_game import record
from helpers.render_fakes import FakeTypedArray, patch_babylon

from core.scenery.ground_boxes import PropPlacement
from render.scenery import imposter_field
from render.scenery.imposter_field import UP_NORMALS, ImposterField, placement_matrix
from render.scenery.imposters import frame_uv, imposter_quad

LOOK = record({"headings": 4, "framePx": 64, "frameSize": 10, "centre": 1.5, "ambient": 0.75})
TILT = math.radians(35)
KINDS = ["car", "van"]


class FakeMesh:
    """A quad mesh: its geometry and material, its vertex data, its uploads and whether it shows."""

    def __init__(self, name: str, geo: Any, material: Any) -> None:
        self.name = name
        self.geo = geo
        self.material = material
        self.vertex_data: dict[str, Any] = {}
        self.uploads: list[list[float]] = []
        self.enabled = False
        self.alwaysSelectAsActiveMesh = False
        self.doNotSyncBoundingInfo = False

    def setVerticesData(self, kind: str, values: Any, updatable: bool) -> None:
        assert not updatable
        self.vertex_data[kind] = values

    def thinInstanceSetBuffer(self, kind: str, buffer: Any, stride: int, static: bool) -> None:
        assert (kind, stride, static) == ("matrix", 16, False)
        self.uploads.append(list(buffer))

    def setEnabled(self, on: bool) -> None:
        self.enabled = on


@pytest.fixture
def field(monkeypatch: pytest.MonkeyPatch) -> ImposterField:
    patch_babylon(monkeypatch, imposter_field)
    monkeypatch.setattr(
        imposter_field,
        "mesh_of",
        lambda name, geo, material, _scene: FakeMesh(name, geo, material),
    )
    return ImposterField("scene", KINDS, LOOK, TILT, "imposter material")


def _mesh(field: ImposterField, kind: str, frame: int) -> FakeMesh:
    mesh: FakeMesh = field._meshes[kind + "#" + str(frame)]
    return mesh


def _car(x: float, rotation: float = 0, kind: str = "car") -> PropPlacement:
    return PropPlacement(kind, x, 2, 30, rotation, 1.5)


def test_d211_a_placement_matrix_scales_and_moves_without_turning() -> None:
    buffer = FakeTypedArray(20)
    placement_matrix(buffer, 4, PropPlacement("car", 1, 2, 3, math.pi / 2, 2))
    assert buffer[0:4] == [0, 0, 0, 0]
    assert buffer[4:20] == [2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 1, 2, 3, 1]


def test_d211_each_kind_has_a_quad_mesh_per_heading(field: ImposterField) -> None:
    names = [mesh.name for mesh in field.meshes]
    assert names == [
        "imposter-car#0",
        "imposter-car#1",
        "imposter-car#2",
        "imposter-car#3",
        "imposter-van#0",
        "imposter-van#1",
        "imposter-van#2",
        "imposter-van#3",
    ]


def test_d211_a_quad_shows_its_frame_of_the_atlas(field: ImposterField) -> None:
    mesh = _mesh(field, "van", 2)
    expected = imposter_quad(LOOK, TILT, frame_uv(LOOK, len(KINDS), 1, 2))
    assert mesh.geo.uvs == expected.uvs
    assert mesh.geo.positions == expected.positions
    assert mesh.material == "imposter material"


def test_perf_26_a_quad_is_lit_from_above_and_always_drawn(field: ImposterField) -> None:
    for mesh in field.meshes:
        assert mesh.vertex_data == {"normal": UP_NORMALS}
        assert mesh.alwaysSelectAsActiveMesh
        assert mesh.doNotSyncBoundingInfo


def test_d211_each_placement_is_drawn_by_the_frame_nearest_its_heading(
    field: ImposterField,
) -> None:
    a, b = _car(1), _car(2)
    turned = _car(3, math.pi / 2)
    field.place([a, turned, b, _car(4, 0, "tank")])
    front = _mesh(field, "car", 0)
    side = _mesh(field, "car", 1)
    scaled = [1.5, 0, 0, 0, 0, 1.5, 0, 0, 0, 0, 1.5, 0]
    assert front.uploads == [[*scaled, 1, 2, 30, 1, *scaled, 2, 2, 30, 1]]
    assert len(side.uploads) == 1
    assert side.uploads[0][12] == 3
    assert front.enabled
    assert side.enabled
    # A kind without imposters is not drawn; frames with nothing to show stay off.
    assert [m.name for m in field.meshes if m.enabled] == ["imposter-car#0", "imposter-car#1"]


def test_d212_unchanged_placements_are_not_uploaded_again(field: ImposterField) -> None:
    cars = [_car(1), _car(2)]
    field.place(cars)
    field.place(list(cars))
    assert len(_mesh(field, "car", 0).uploads) == 1
    field.place([cars[0]])
    assert len(_mesh(field, "car", 0).uploads) == 2


def test_d212_a_frame_left_with_nothing_to_show_is_turned_off_once(field: ImposterField) -> None:
    field.place([_car(1)])
    mesh = _mesh(field, "car", 0)
    field.place([])
    assert not mesh.enabled
    assert field._drawn["car#0"] == []
    mesh.enabled = True
    # Already off: not turned off again.
    field.place([])
    assert mesh.enabled
