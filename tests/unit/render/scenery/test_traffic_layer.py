"""Unit tests of `src/render/scenery/traffic_layer.py`."""

from types import SimpleNamespace
from typing import Any

import pytest

from render.scenery import traffic_layer
from render.scenery.traffic_layer import TrafficLayer, TrafficSource, _goes_on


class _Field:
    """A prop field of the cars: the chunks it was given, and the syncs."""

    instances: list["_Field"] = []

    def __init__(
        self, scene: Any, models: Any, materials: Any, on_structure: Any, plumes: Any
    ) -> None:
        self.models = models
        self.chunks: list[tuple[int, list[Any]]] = []
        self.syncs = 0
        self.light_meshes = ["headlight"]
        self.structure_meshes = ["body"]
        self.count = 0
        _Field.instances.append(self)

    def set_chunk(self, index: int, cars: list[Any]) -> None:
        self.chunks.append((index, cars))

    def sync(self) -> None:
        self.syncs += 1


class _Traffic:
    """The traffic of some roads: the cars it places, and the roads it was given later."""

    made: list["_Traffic"] = []

    def __init__(self, roads: list[Any], height: Any, rules: Any, seed: int) -> None:
        self.roads = roads
        self.height = height
        self.rules = rules
        self.seed = seed
        self.added: list[list[Any]] = []
        self.areas: list[Any] = []
        _Traffic.made.append(self)

    def at(self, time: float, area: Any) -> list[str]:
        self.areas.append((time, area))
        return ["car-at-" + str(time)]

    def add(self, roads: list[Any]) -> None:
        self.added.append(roads)


@pytest.fixture(autouse=True)
def _fakes(monkeypatch: pytest.MonkeyPatch) -> None:
    _Field.instances = []
    _Traffic.made = []
    monkeypatch.setattr(traffic_layer, "PropField", _Field)
    monkeypatch.setattr(traffic_layer, "Traffic", _Traffic)


def _rules(*kinds: str) -> SimpleNamespace:
    return SimpleNamespace(kinds=list(kinds))


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
    assert field.chunks == []
    assert field.syncs == 0
    assert _Traffic.made == []


def test_the_field_forwards_its_lights_structure_and_count() -> None:
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    field = _Field.instances[0]
    field.count = 4
    assert layer.light_meshes == ["headlight"]
    assert layer.structure_meshes == ["body"]
    assert layer.count == 4


def test_the_first_update_makes_the_traffic_of_the_roads_and_places_its_cars() -> None:
    layer = TrafficLayer(None, {"car": "m"}, "materials", _rules("car"))
    roads = ["road-a"]
    height = object()
    layer.update(2.0, "view", TrafficSource(roads, height, 99))
    traffic = _Traffic.made[0]
    assert (traffic.roads, traffic.height, traffic.seed) == (roads, height, 99)
    assert traffic.areas == [(2.0, "view")]
    field = _Field.instances[0]
    assert field.chunks == [(0, ["car-at-2.0"])]
    assert field.syncs == 1


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
