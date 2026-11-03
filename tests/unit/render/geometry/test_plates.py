# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/plates.py`: an outline cracked into plates (BOSS-43)."""

import pytest

from render.geometry import plates
from render.geometry.plates import crack, roughen, subdivide
from render.geometry.triangulate import triangulate_polygon

RECT = [[-28.0, -35.0], [28.0, -35.0], [28.0, 21.0], [-28.0, 21.0]]
ELL = [[0.0, 0.0], [40.0, 0.0], [40.0, 10.0], [10.0, 10.0], [10.0, 30.0], [0.0, 30.0]]


def _area(ring: list) -> float:
    return plates._double_area(ring) / 2


def _inside(ring: list, x: float, z: float) -> bool:
    result = False
    n = len(ring)
    for i in range(n):
        a = ring[i]
        b = ring[(i + n - 1) % n]
        if (a[1] > z) != (b[1] > z):
            cross = a[0] + (z - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < cross:
                result = not result
    return result


def test_the_plates_cover_the_outline_in_at_most_the_count_asked() -> None:
    for outline, most in [(RECT, 12), (ELL, 5), (RECT, 1)]:
        result = crack(outline, 18, most)
        assert 1 <= len(result) <= most
        assert sum(_area(p) for p in result) == pytest.approx(abs(_area(outline)))
        for plate in result:
            # A simple, counter-clockwise polygon, every corner of it in the outline.
            assert _area(plate) > 0
            assert len(plate) >= 3
            for x, z in plate:
                assert _inside(outline, x, z) or any(
                    abs(x - ox) < 1e-6 or abs(z - oz) < 1e-6 for ox, oz in outline
                )


def test_a_clockwise_outline_cracks_like_its_reverse() -> None:
    assert sum(_area(p) for p in crack(list(reversed(RECT)), 18, 6)) == pytest.approx(_area(RECT))


def test_a_tiny_outline_is_one_plate() -> None:
    [plate] = crack([[0.0, 0.0], [3.0, 0.0], [3.0, 3.0]], 10, 4)
    assert _area(plate) == 4.5


def test_subdivide_cuts_every_triangle_down_to_the_cell() -> None:
    tris = [[[0.0, 0.0], [40.0, 0.0], [0.0, 40.0]]]
    small = subdivide(tris, 12)
    assert len(small) == 64
    assert all(plates._longest_edge(t) <= 12 for t in small)
    assert sum(_area(t) for t in small) == pytest.approx(800)
    assert subdivide(small, 12) == small


def test_roughen_moves_only_the_inner_corners_and_keeps_them_shared() -> None:
    tris = subdivide([[[0.0, 0.0], [40.0, 0.0], [0.0, 40.0]]], 12)
    rough = roughen(tris, 3)
    moved = 0
    seen: dict[str, list[float]] = {}
    for before, after in zip(tris, rough, strict=True):
        for p, q in zip(before, after, strict=True):
            on_edge = p[0] == 0 or p[1] == 0 or p[0] + p[1] == 40
            if on_edge:
                assert q == p
            elif q != p:
                moved += 1
                assert abs(q[0] - p[0]) <= 1.5
                assert abs(q[1] - p[1]) <= 1.5
            key = plates._key(p)
            assert seen.setdefault(key, q) == q
    assert moved > 0
    assert sum(_area(t) for t in rough) == pytest.approx(800)


def test_a_small_group_that_touches_no_other_stays_a_plate_of_its_own() -> None:
    # Three triangles: two neighbours in group 0, an island in group 1.
    neighbours = [[1], [0], []]
    assert plates._merge_small([0, 0, 1], neighbours, 2) == [0, 0, 1]
    # A small group beside another is merged into it.
    assert plates._merge_small([0, 1, 1], [[1], [0, 2], [1]], 2) == [1, 1, 1]
    # Over the cap, the smallest groups go into their neighbours; an island is left alone.
    assert plates._merge_down([0, 1, 1, 2], [[1], [0, 2], [1], []], 1) == [1, 1, 1, 2]


def test_a_boundary_pinched_at_a_corner_makes_two_simple_loops() -> None:
    # Two triangles touching at the origin only: a bow tie.
    tris = [
        [[0.0, 0.0], [2.0, 0.0], [0.0, 2.0]],
        [[0.0, 0.0], [-2.0, 0.0], [0.0, -2.0]],
    ]
    loops = plates._loops(tris)
    assert len(loops) == 2
    assert all(len(loop) == 3 for loop in loops)
    assert sum(_area(loop) for loop in loops) == pytest.approx(4)
    # A corner on the line between its neighbours is dropped.
    assert plates._without_collinear([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [2.0, 2.0]]) == [
        [0.0, 0.0],
        [2.0, 0.0],
        [2.0, 2.0],
    ]


def test_every_plate_of_a_lozenge_is_a_simple_polygon() -> None:
    lozenge = [
        [0.0, 24.0],
        [-7.0, 20.0],
        [-12.5, 12.0],
        [-14.0, 0.0],
        [-12.5, -12.0],
        [-7.0, -22.0],
    ]
    lozenge.extend([
        [0.0, -28.0],
        [7.0, -22.0],
        [12.5, -12.0],
        [14.0, 0.0],
        [12.5, 12.0],
        [7.0, 20.0],
    ])
    result = crack(lozenge, 52 / 3, 12)
    assert 1 <= len(result) <= 12
    assert sum(_area(p) for p in result) == pytest.approx(abs(_area(lozenge)))
    for plate in result:
        assert triangulate_polygon(plate)


def test_the_boundary_of_a_ring_of_triangles_drops_its_hole() -> None:
    outer = [[0.0, 0.0], [3.0, 0.0], [3.0, 3.0], [0.0, 3.0]]
    inner = [[1.0, 1.0], [2.0, 1.0], [2.0, 2.0], [1.0, 2.0]]
    tris = []
    for i in range(4):
        a, b = outer[i], outer[(i + 1) % 4]
        c, d = inner[i], inner[(i + 1) % 4]
        tris.extend([[a, b, d], [a, d, c]])
    [loop] = plates._loops(tris)
    assert _area(loop) == 9
    assert len(loop) == 4
