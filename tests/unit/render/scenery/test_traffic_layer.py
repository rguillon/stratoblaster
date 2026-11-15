# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/traffic_layer.py` (GFX-CAR-05, GFX-CAR-08, PERF-27, D-422)."""

import math
from types import SimpleNamespace
from typing import Any, ClassVar

import pytest
from helpers.render_fakes import FakeTypedArray, patch_babylon

from core.scenery.ground_boxes import PropPlacement
from core.scenery.traffic import CAR_VALUES
from render.scenery import traffic_layer
from render.scenery.imposter_field import placement_matrix
from render.scenery.imposters import frame_of
from render.scenery.traffic_layer import (
    FIRST_ROOM,
    InstanceBatch,
    TrafficLayer,
    TrafficSource,
    _goes_on,
    turned_matrix,
    upright_matrix,
)

SCALE = 1.5


class _Field:
    """A prop field of the cars: the matrices each kind was drawn with, call after call."""

    instances: ClassVar[list["_Field"]] = []

    def __init__(
        self, _scene: Any, models: Any, _materials: Any, _on_structure: Any, _plumes: Any
    ) -> None:
        self.models = models
        self.draws: list[tuple[str, list[float]]] = []
        self.light_meshes = ["headlight"]
        self.structure_meshes = ["body"]
        _Field.instances.append(self)

    def draw_kind(self, kind: str, matrices: Any) -> None:
        self.draws.append((kind, list(matrices)))


class _Traffic:
    """The traffic of some roads: the cars it places, and the roads it was given later."""

    made: ClassVar[list["_Traffic"]] = []
    # The cars the next `fill` puts in view: (kind index, x, y, z, rotation) each.
    cars: ClassVar[list[tuple[float, ...]]] = []

    def __init__(self, roads: list[Any], height: Any, rules: Any, seed: int) -> None:
        self.roads = roads
        self.height = height
        self.rules = rules
        self.seed = seed
        self.added: list[list[Any]] = []
        self.areas: list[Any] = []
        _Traffic.made.append(self)

    def fill(self, time: float, area: Any, cars: Any) -> None:
        self.areas.append((time, area))
        cars.values.clear()
        for car in _Traffic.cars:
            cars.values.extend(car)
        cars.count = len(_Traffic.cars)

    def add(self, roads: list[Any]) -> None:
        self.added.append(roads)


@pytest.fixture(autouse=True)
def _fakes(monkeypatch: pytest.MonkeyPatch) -> None:
    _Field.instances = []
    _Traffic.made = []
    _Traffic.cars = []
    patch_babylon(monkeypatch, traffic_layer)
    monkeypatch.setattr(traffic_layer, "PropField", _Field)
    monkeypatch.setattr(traffic_layer, "Traffic", _Traffic)


def _rules(*kinds: str) -> SimpleNamespace:
    return SimpleNamespace(kinds=list(kinds), scale=SCALE)


def _turned(x: float, y: float, z: float, rotation: float) -> list[float]:
    """Return the matrix `turned_matrix` writes for a car there."""
    floats = FakeTypedArray(16)
    turned_matrix(floats, 0, [0, x, y, z, rotation], 0, SCALE)
    return list(floats)


def _upright(x: float, y: float, z: float) -> list[float]:
    return [SCALE, 0, 0, 0, 0, SCALE, 0, 0, 0, 0, SCALE, 0, x, y, z, 1]


def _babylon_matrix(p: PropPlacement) -> list[float]:
    """Return the world matrix Babylon composes for `p`: its own formulas, written out.

    `Quaternion.RotationYawPitchRollToRef(yaw, 0, 0)` then `Matrix.ComposeToRef(scale, turn,
    position)`, as `prop_field.instance_matrices` calls them.
    """
    half_roll, half_pitch, half_yaw = 0.0, 0.0, p.rotation * 0.5
    sin_roll, cos_roll = math.sin(half_roll), math.cos(half_roll)
    sin_pitch, cos_pitch = math.sin(half_pitch), math.cos(half_pitch)
    sin_yaw, cos_yaw = math.sin(half_yaw), math.cos(half_yaw)
    x = cos_yaw * sin_pitch * cos_roll + sin_yaw * cos_pitch * sin_roll
    y = sin_yaw * cos_pitch * cos_roll - cos_yaw * sin_pitch * sin_roll
    z = cos_yaw * cos_pitch * sin_roll - sin_yaw * sin_pitch * cos_roll
    w = cos_yaw * cos_pitch * cos_roll + sin_yaw * sin_pitch * sin_roll
    x2, y2, z2 = x + x, y + y, z + z
    xx, xy, xz = x * x2, x * y2, x * z2
    yy, yz, zz = y * y2, y * z2, z * z2
    wx, wy, wz = w * x2, w * y2, w * z2
    sx = sy = sz = p.scale
    return [
        (1 - (yy + zz)) * sx,
        (xy + wz) * sx,
        (xz - wy) * sx,
        0,
        (xy - wz) * sy,
        (1 - (xx + zz)) * sy,
        (yz + wx) * sy,
        0,
        (xz + wy) * sz,
        (yz - wx) * sz,
        (1 - (xx + yy)) * sz,
        0,
        p.x,
        p.y,
        p.z,
        1,
    ]


def test_d422_a_car_s_matrix_is_the_one_babylon_composes_to_the_last_bit() -> None:
    """PERF-03: the same numbers as the quaternion and `ComposeToRef` gave, without them."""
    for rotation in [0.0, 0.3, math.pi / 2, math.pi, -2.2, 5.9, math.atan2(0.3, -0.8) + math.pi]:
        for scale in [1.0, 1.5, 0.37]:
            p = PropPlacement("car", 12.5, -3.25, 987.125, rotation, scale)
            floats = FakeTypedArray(20)
            turned_matrix(floats, 4, [7, p.x, p.y, p.z, p.rotation], 0, scale)
            assert floats[0:4] == [0, 0, 0, 0]
            assert floats[4:20] == _babylon_matrix(p)


def test_d422_a_car_s_imposter_matrix_is_the_placement_matrix_of_the_imposter_field() -> None:
    p = PropPlacement("car", 4, 5, 6, 1.1, SCALE)
    expected = FakeTypedArray(32)
    placement_matrix(expected, 16, p)
    floats = FakeTypedArray(32)
    # The car at float 5 of the values: after one other car.
    upright_matrix(floats, 16, [0, 0, 0, 0, 0, 3, p.x, p.y, p.z, p.rotation], CAR_VALUES, SCALE)
    assert list(floats) == list(expected)


def test_d422_a_batch_starts_empty_with_room_for_some_matrices() -> None:
    batch = InstanceBatch()
    assert len(batch.floats) == FIRST_ROOM * 16
    assert batch.count == 0
    assert batch.shown is False


def test_a_traffic_source_holds_its_roads_height_function_and_seed() -> None:
    def height(x: float, z: float) -> float:
        return x + z

    roads = ["road"]
    source = TrafficSource(roads, height, 17)
    assert source.roads is roads
    assert source.height is height
    assert source.seed == 17


@pytest.mark.parametrize(
    ("before", "roads", "expected"),
    [
        ([], ["a"], True),
        (["a", "b"], ["a", "b"], True),
        (["a", "b"], ["a", "b", "c"], True),
        (["a", "b"], ["a"], False),
        (["a", "b"], ["b", "a", "c"], False),
    ],
)
def test_roads_go_on_when_they_start_with_the_same_roads(
    before: list[str], roads: list[str], expected: bool
) -> None:
    assert _goes_on(before, roads) is expected


def test_roads_that_only_look_the_same_do_not_go_on_from_the_others() -> None:
    first, second = ["x"], ["x"]
    assert _goes_on([first], [second]) is False


def test_the_cars_are_the_models_of_the_kinds_the_rules_allow() -> None:
    TrafficLayer(None, {"car": "car-model", "tree": "tree-model"}, "materials", _rules("car"))
    field = _Field.instances[0]
    assert field.models == {"car": "car-model"}


def test_a_level_without_cars_has_no_cars_and_updates_nothing() -> None:
    layer = TrafficLayer(None, {"car": "car-model"}, "materials", None)
    layer.update(5.0, "area", TrafficSource(["road"], None, 1))
    field = _Field.instances[0]
    assert field.models == {}
    assert field.draws == []
    assert _Traffic.made == []
    assert layer.count == 0


def test_the_field_forwards_its_lights_and_structure_and_the_count_is_the_cars_in_view() -> None:
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    assert layer.light_meshes == ["headlight"]
    assert layer.structure_meshes == ["body"]
    assert layer.count == 0
    _Traffic.cars = [(0, 1, 2, 3, 0.5), (0, 4, 5, 6, 0.5), (0, 7, 8, 9, 0.5)]
    layer.update(1.0, "view", TrafficSource(["road"], None, 1))
    assert layer.count == 3


def test_the_first_update_makes_the_traffic_of_the_roads_and_places_its_cars() -> None:
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    roads = ["road-a"]
    height = object()
    _Traffic.cars = [(0, 1, 2, 3, 0.25)]
    layer.update(2.0, "view", TrafficSource(roads, height, 99))
    traffic = _Traffic.made[0]
    assert (traffic.roads, traffic.height, traffic.seed) == (roads, height, 99)
    assert traffic.areas == [(2.0, "view")]
    field = _Field.instances[0]
    assert field.draws == [("car", _turned(1, 2, 3, 0.25))]


def test_d422_the_cars_of_a_kind_are_drawn_together_in_road_order_kind_by_kind() -> None:
    layer = TrafficLayer(None, {"car": "m", "van": "v"}, "materials", _rules("car", "van"))
    _Traffic.cars = [(1, 1, 0, 10, 0.1), (0, 2, 0, 20, 0.2), (1, 3, 0, 30, 0.3), (0, 4, 0, 40, 0.4)]
    layer.update(1.0, "view", TrafficSource(["road"], None, 1))
    field = _Field.instances[0]
    assert field.draws == [
        ("car", _turned(2, 0, 20, 0.2) + _turned(4, 0, 40, 0.4)),
        ("van", _turned(1, 0, 10, 0.1) + _turned(3, 0, 30, 0.3)),
    ]


def test_d422_a_kind_left_without_cars_is_hidden_once_and_one_never_seen_is_left_alone() -> None:
    layer = TrafficLayer(None, {"car": "m", "van": "v"}, "materials", _rules("car", "van"))
    source = TrafficSource(["road"], None, 1)
    _Traffic.cars = [(0, 1, 2, 3, 0.0)]
    layer.update(1.0, "view", source)
    _Traffic.cars = []
    layer.update(2.0, "view", source)
    layer.update(3.0, "view", source)
    field = _Field.instances[0]
    # The van never showed: nothing to hide. The car is hidden by an upload of no matrix, once.
    assert field.draws == [("car", _turned(1, 2, 3, 0.0)), ("car", [])]
    assert layer.count == 0


def test_d422_a_batch_grows_when_full_and_keeps_its_matrices() -> None:
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    count = 2 * FIRST_ROOM + 3
    _Traffic.cars = [(0, i, 0, 2 * i, 0.1 * i) for i in range(count)]
    layer.update(1.0, "view", TrafficSource(["road"], None, 1))
    field = _Field.instances[0]
    expected: list[float] = []
    for i in range(count):
        expected.extend(_turned(i, 0, 2 * i, 0.1 * i))
    assert field.draws == [("car", expected)]
    # The buffer doubled twice, and is kept: fewer cars the next frame use its start.
    assert len(layer._batches[0].floats) == 4 * FIRST_ROOM * 16
    _Traffic.cars = [(0, 5, 6, 7, 0.0)]
    layer.update(2.0, "view", TrafficSource(["road"], None, 1))
    assert field.draws[1] == ("car", _turned(5, 6, 7, 0.0))
    assert len(layer._batches[0].floats) == 4 * FIRST_ROOM * 16


def test_the_same_roads_keep_their_traffic_across_updates() -> None:
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    roads = ["road-a"]
    layer.update(1.0, "view", TrafficSource(roads, None, 1))
    layer.update(2.0, "view", TrafficSource(roads, None, 1))
    assert len(_Traffic.made) == 1
    assert _Traffic.made[0].areas == [(1.0, "view"), (2.0, "view")]


def test_roads_that_go_on_from_the_ones_before_only_add_their_traffic() -> None:
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    first = "road-a"
    layer.update(1.0, "view", TrafficSource([first], None, 1))
    extended = [first, "road-b", "road-c"]
    layer.update(2.0, "view", TrafficSource(extended, None, 1))
    assert len(_Traffic.made) == 1
    assert _Traffic.made[0].added == [["road-b", "road-c"]]


def test_new_roads_that_do_not_go_on_get_new_traffic() -> None:
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    layer.update(1.0, "view", TrafficSource(["road-a"], None, 1))
    layer.update(2.0, "view", TrafficSource(["road-z"], None, 2))
    assert len(_Traffic.made) == 2
    assert _Traffic.made[1].seed == 2
    assert _Traffic.made[1].added == []


class _ImposterField:
    """The quads of the cars' imposters: the matrices each frame of a kind was drawn with."""

    def __init__(self) -> None:
        self.draws: list[tuple[str, int, list[float]]] = []

    def draw_frame(self, kind: str, frame: int, matrices: Any) -> None:
        self.draws.append((kind, frame, list(matrices)))


class _Imposters:
    """The cars' imposters (D-211): their models, their headings, their field and the bakes."""

    def __init__(self, models: Any, headings: int) -> None:
        self.models = models
        self.headings = headings
        self.field = _ImposterField()
        self.bakes = 0

    def bake_once(self) -> None:
        self.bakes += 1


def _with_imposters(monkeypatch: pytest.MonkeyPatch, kinds: list[str]) -> Any:
    imposters = _Imposters({k: k + "-lights-only" for k in kinds}, 4)
    asked: list[tuple[Any, ...]] = []

    def fake_imposter_kinds(*args: Any) -> _Imposters:
        asked.append(args)
        return imposters

    monkeypatch.setattr(traffic_layer, "imposter_kinds", fake_imposter_kinds)
    return imposters, asked


def test_d211_cars_drawn_as_imposters_are_baked_on_update_and_placed_with_their_lights(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GFX-CAR-05."""
    imposters, asked = _with_imposters(monkeypatch, ["car"])
    layer = TrafficLayer(
        "scene", {"car": "m", "tree": "t"}, "materials", _rules("car"), "atlas-of", 0.3
    )
    assert asked == [("scene", {"car": "m"}, ["car"], "atlas-of", 0.3)]
    # The field draws the imposters' models (the cars' lights), not the detailed ones.
    field = _Field.instances[0]
    assert field.models == {"car": "car-lights-only"}
    # Nothing is baked when made: the bake's mesh must not hang from the ground.
    assert imposters.bakes == 0
    _Traffic.cars = [(0, 1, 2, 3, 0.0)]
    layer.update(1.0, "view", TrafficSource(["road-a"], None, 1))
    assert imposters.bakes == 1
    # Its lights turned as the car, its picture upright, in the frame of its heading.
    assert field.draws == [("car", _turned(1, 2, 3, 0.0))]
    assert imposters.field.draws == [("car", 0, _upright(1, 2, 3))]


def test_d422_each_imposter_is_drawn_by_the_frame_nearest_its_heading_in_road_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imposters, _asked = _with_imposters(monkeypatch, ["car", "van"])
    layer = TrafficLayer(None, {"car": "m", "van": "v"}, "materials", _rules("car", "van"))
    side = math.pi / 2
    assert frame_of(side, 4) == 1
    _Traffic.cars = [
        (1, 1, 0, 10, side),
        (0, 2, 0, 20, 0.0),
        (1, 3, 0, 30, side),
        (0, 4, 0, 40, side),
    ]
    layer.update(1.0, "view", TrafficSource(["road"], None, 1))
    assert imposters.field.draws == [
        ("car", 0, _upright(2, 0, 20)),
        ("car", 1, _upright(4, 0, 40)),
        ("van", 1, _upright(1, 0, 10) + _upright(3, 0, 30)),
    ]


def test_d422_an_imposter_frame_left_without_cars_is_hidden_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    imposters, _asked = _with_imposters(monkeypatch, ["car"])
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    source = TrafficSource(["road"], None, 1)
    _Traffic.cars = [(0, 1, 2, 3, 0.0)]
    layer.update(1.0, "view", source)
    # The car has turned: its old frame is hidden, its new one drawn.
    _Traffic.cars = [(0, 1, 2, 3, math.pi)]
    layer.update(2.0, "view", source)
    layer.update(3.0, "view", source)
    assert imposters.field.draws == [
        ("car", 0, _upright(1, 2, 3)),
        ("car", 0, []),
        ("car", 2, _upright(1, 2, 3)),
        ("car", 2, _upright(1, 2, 3)),
    ]
    assert imposters.bakes == 3
