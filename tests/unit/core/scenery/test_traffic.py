"""Unit tests of `src/core/scenery/traffic.py`."""

import math

from core.scenery.ground_boxes import GroundArea
from core.scenery.road_types import Road, RoadPoint
from core.scenery.scenery_level import CarRules
from core.scenery.traffic import Traffic

FAR = GroundArea(-1000, 1000, -1000, 5000)


def straight(
    index: int,
    kind: str = "main",
    length: float = 380,
    width: float = 6,
    lanes: int = 1,
    step: float = 20,
) -> Road:
    """A road along Z at X = 0, one point every `step` units."""
    count = int(length / step) + 1
    points = [RoadPoint(0, i * step, width) for i in range(count)]
    return Road(index, kind, width, lanes, points)


def rules(**overrides: object) -> CarRules:
    """One car kind, a car at every point, at 20 units per second."""
    values: dict[str, object] = {
        "kinds": ["car"],
        "density": 1,
        "lift": 0.5,
        "scale": 1,
        "length": 10,
        "speed": [20, 20],
    }
    values.update(overrides)
    return CarRules(**values)  # type: ignore[arg-type]


def ground(x: float, z: float) -> float:
    return 2.0


def test_a_car_starts_at_every_point_with_the_density() -> None:
    road = straight(0)
    assert Traffic([road], ground, rules(), 1).count == len(road.points)
    assert Traffic([road], ground, rules(density=0), 1).count == 0


def test_cars_need_a_kind_and_skip_paths_and_single_point_roads() -> None:
    assert Traffic([straight(0)], ground, rules(kinds=[]), 1).count == 0
    assert Traffic([straight(0, kind="cross")], ground, rules(), 1).count == 0
    lone = Road(1, "main", 6, 1, [RoadPoint(0, 0, 6)])
    assert Traffic([lone], ground, rules(), 1).count == 0


def test_add_takes_the_cars_of_later_roads() -> None:
    traffic = Traffic([straight(0)], ground, rules(), 1)
    before = traffic.count
    traffic.add([straight(1, length=100)])
    assert traffic.count > before


def test_cars_drive_in_their_lane_on_the_road_and_face_the_way_they_drive() -> None:
    traffic = Traffic([straight(0)], ground, rules(), 1)
    cars = traffic.at(3.0, FAR)
    assert cars
    for car in cars:
        assert abs(abs(car.x) - 1.5) < 1e-9
        assert car.y == 2.5
        assert car.rotation in (0, math.pi)
        assert car.kind == "car"
        assert car.scale == 1


def test_cars_are_hidden_near_the_ends_of_their_road() -> None:
    cars = Traffic([straight(0)], ground, rules(), 1).at(7.0, FAR)
    assert cars
    assert all(10 - 1e-9 <= car.z <= 370 + 1e-9 for car in cars)


def test_cars_wrap_round_their_road_and_keep_to_it() -> None:
    later = Traffic([straight(0)], ground, rules(), 1).at(1000.0, FAR)
    assert later
    assert all(10 - 1e-9 <= car.z <= 370 + 1e-9 for car in later)


def test_the_same_seed_gives_the_same_cars() -> None:
    first = Traffic([straight(0)], ground, rules(), 4).at(5.0, FAR)
    second = Traffic([straight(0)], ground, rules(), 4).at(5.0, FAR)
    assert [(c.x, c.z, c.rotation) for c in first] == [(c.x, c.z, c.rotation) for c in second]
    other = Traffic([straight(0)], ground, rules(), 5).at(5.0, FAR)
    assert [(c.x, c.z) for c in other] != [(c.x, c.z) for c in first]


def test_cars_stay_out_of_areas_without_roads() -> None:
    traffic = Traffic([straight(0)], ground, rules(), 1)
    assert traffic.at(3.0, GroundArea(500, 600, 0, 100)) == []


def test_a_car_in_a_long_road_is_listed_once_across_buckets() -> None:
    long_road = straight(0, length=1000)
    traffic = Traffic([long_road], ground, rules(), 1)
    cars = traffic.at(0.0, FAR)
    positions = [(c.x, c.z) for c in cars]
    assert len(set(positions)) == len(positions)
    narrow = traffic.at(0.0, GroundArea(-1000, 1000, 300, 340))
    assert narrow
    assert all(300 <= c.z < 340 for c in narrow)
    assert len({(c.x, c.z) for c in narrow}) == len(narrow)


def test_p15_r11_streets_keep_their_cars_off_the_sidewalks() -> None:
    street = straight(0, kind="street", width=10)
    with_walk = Traffic([street], ground, rules(sidewalk=2), 1).at(3.0, FAR)
    assert with_walk
    assert all(abs(abs(c.x) - 1.5) < 1e-9 for c in with_walk)
    no_walk = Traffic([street], ground, rules(), 1).at(3.0, FAR)
    assert all(abs(abs(c.x) - 2.5) < 1e-9 for c in no_walk)


def test_two_lanes_each_way_put_cars_at_two_offsets() -> None:
    two = straight(0, width=6, lanes=2)
    cars = Traffic([two], ground, rules(), 2).at(3.0, FAR)
    assert cars
    # Lane 0 is 0.75 from the centre line, lane 1 is 2.25 (each lane 3 wide).
    assert {round(abs(c.x), 6) for c in cars} <= {0.75, 2.25}
