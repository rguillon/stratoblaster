"""The data of the road network (`core/scenery/road_types.py`)."""

from core.scenery.road_types import Road, RoadPoint, RoadSlot, RoadSnapshot


def test_road_keeps_its_points_and_lanes() -> None:
    points = [RoadPoint(0.0, 0.0, 24.0), RoadPoint(0.0, 10.0, 24.0)]
    road = Road(3, "street", 24.0, 1, points)
    assert (road.index, road.kind, road.width, road.lanes) == (3, "street", 24.0, 1)
    assert road.points is points


def test_slot_and_snapshot_hold_what_they_are_given() -> None:
    road = Road(0, "main", 24.0, 1, [])
    slot = RoadSlot(road, 2, 1.0, 2.0, 0.0, -1.0)
    assert (slot.road, slot.index, slot.x, slot.z, slot.nx, slot.nz) == (
        road,
        2,
        1.0,
        2.0,
        0.0,
        -1.0,
    )
    snapshot = RoadSnapshot([road], [], [slot])
    assert snapshot.roads == [road]
    assert snapshot.blocks == []
    assert snapshot.slots == [slot]
