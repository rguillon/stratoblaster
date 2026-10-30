"""Boxes of ground props take, and the index of placed buildings (`core.scenery.ground_boxes`)."""

from core.scenery.ground_boxes import (
    BUILDING_BUCKET,
    BuildingIndex,
    GroundArea,
    PlacerSnapshot,
    PropPlacement,
    _to_bucket,
    inside,
    overlap,
)


class Box:
    """A building for the index: its prop's place and the half-extents of its ground."""

    def __init__(self, x: float, z: float, half_x: float, half_z: float | None = None) -> None:
        self.placement = PropPlacement("block", x, 0, z, 0, 1)
        self.half_x = half_x
        self.half_z = half_x if half_z is None else half_z


def test_inside_excludes_the_far_edges() -> None:
    area = GroundArea(0, 10, 0, 20)
    assert inside(area, 0, 0)
    assert inside(area, 9.9, 19.9)
    assert not inside(area, 10, 5)
    assert not inside(area, 5, 20)
    assert not inside(area, -0.1, 5)


def test_overlap_needs_both_axes_closer_than_the_sum_of_the_halves() -> None:
    a = Box(0, 0, 2)
    assert overlap(a, Box(3, 0, 2), 0)
    assert not overlap(a, Box(4, 0, 2), 0)
    # Apart on X only: they do not overlap, however close on Z.
    assert not overlap(a, Box(10, 0, 2), 0)
    assert not overlap(a, Box(0, 10, 2), 0)


def test_overlap_keeps_the_gap_clear() -> None:
    a = Box(0, 0, 2)
    assert not overlap(a, Box(4, 0, 2), 0)
    assert overlap(a, Box(4, 0, 2), 0.5)
    assert overlap(Box(0, 0, 2, 1), Box(2.5, 0, 1, 2), 0)
    assert not overlap(Box(0, 0, 2, 1), Box(3, 0, 1, 2), 0)


def test_index_finds_a_building_close_by_and_not_one_far_away() -> None:
    index = BuildingIndex()
    index.add(Box(0, 0, 5))
    assert not index.clear(Box(5, 0, 1), 0)
    assert index.clear(Box(6, 0, 1), 0)
    assert index.clear(Box(0, 100, 1), 0)
    assert index.clear(Box(200, 200, 1), 1)


def test_index_respects_the_gap_when_clearing() -> None:
    index = BuildingIndex()
    index.add(Box(0, 0, 5))
    # Ten units between the centres, 1 + 5 = 6 half-extents: 4 units apart.
    assert index.clear(Box(10, 0, 1), 0)
    assert index.clear(Box(10, 0, 1), 4)
    assert not index.clear(Box(10, 0, 1), 5)


def test_index_checks_buildings_in_neighbouring_buckets() -> None:
    index = BuildingIndex()
    # The building's centre is in bucket 0, the query's in bucket 1: the next one over.
    index.add(Box(BUILDING_BUCKET - 1, 0, 1))
    assert not index.clear(Box(BUILDING_BUCKET + 0.5, 0, 1), 0)


def test_index_skips_buckets_too_far_for_their_largest_building() -> None:
    index = BuildingIndex()
    index.add(Box(0, 0, 1))
    # Two buckets over on X, and on Z: both are looked at, and both are too far to matter.
    assert index.clear(Box(2 * BUILDING_BUCKET + 10, 0, 1), 0)
    assert index.clear(Box(0, 2 * BUILDING_BUCKET + 10, 1), 0)
    assert index.clear(Box(-2 * BUILDING_BUCKET - 10, 0, 1), 0)


def test_index_grows_a_bucket_with_its_largest_building() -> None:
    index = BuildingIndex()
    index.add(Box(1, 1, 2, 3))
    index.add(Box(2, 2, 6, 1))
    bucket = index._buckets[next(iter(index._buckets))]
    assert bucket.half_x == 6
    assert bucket.half_z == 3
    assert len(bucket.buildings) == 2


def test_index_is_empty_clear() -> None:
    assert BuildingIndex().clear(Box(0, 0, 1), 10)


def test_to_bucket_is_the_distance_to_the_bucket_along_one_axis() -> None:
    assert _to_bucket(5, 0) == 0
    assert _to_bucket(-4, 0) == 4
    assert _to_bucket(40, 0) == 8
    assert _to_bucket(40, 1) == 0


def test_placer_snapshot_keeps_its_fields() -> None:
    snapshot = PlacerSnapshot([], 2, 3)
    assert (snapshot.buildings, snapshot.fixed, snapshot.placed_to) == ([], 2, 3)


def test_index_finds_a_huge_building_whose_bucket_is_two_or_more_away() -> None:
    # A building wider than two buckets (BUILDING_BUCKET) whose centre lies further off must not be
    # missed: the index searches as far as its largest building reaches. Its centre is at X = 100
    # (bucket 3), half 100, so it reaches X = 0; the query box at X = -1 with half 1 and gap 1
    # overlaps it (|dx| = 101 < 102).
    index = BuildingIndex()
    index.add(Box(100, 0, 100))
    assert not index.clear(Box(-1, 0, 1), 1)
