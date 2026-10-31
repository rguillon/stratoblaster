"""Unit tests of `src/render/geometry/shatter.py`: carving a boss's armour out of its body and
breaking it into chunks (docs/superpowers/specs/2026-10-31-boss-armour-shedding-design.md)."""

from render.geometry.shatter import (
    Carve,
    carve,
    centroid,
    chunk_cells,
    geometry_of,
    inside,
    Vertex,
    shatter,
    straddles,
    subdivide,
    triangles,
    up_facing,
)
from render.geometry.solids import Placement, SolidBuilder

WHITE = [1.0, 1.0, 1.0]
SQUARE = [[-10.0, -10.0], [10.0, -10.0], [10.0, 10.0], [-10.0, 10.0]]


def _slab(size: float = 40.0) -> list:
    return triangles(SolidBuilder().box([size, 2, size], WHITE, Placement([0, 0, 0])).geometry)


def _area(tris: list) -> float:
    total = 0.0
    for t in tris:
        a, b, c = (v.position for v in t)
        u = [b[i] - a[i] for i in range(3)]
        v = [c[i] - a[i] for i in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        total += (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5 / 2
    return total


def test_triangles_and_geometry_of_round_trip_a_geometry() -> None:
    tris = _slab()
    geo = geometry_of(tris)
    assert len(geo.indices) == 3 * len(tris)
    assert len(geo.colors) == 4 * len(geo.positions) // 3
    assert _area(triangles(geo)) == _area(tris)


def test_geometry_of_moves_the_triangles_by_the_shift() -> None:
    geo = geometry_of(_slab(), [1, 2, 3])
    xs = geo.positions[0::3]
    assert min(xs) == -19 and max(xs) == 21


def test_subdivide_cuts_every_edge_down_and_keeps_the_area_and_facing() -> None:
    tris = _slab()
    small = subdivide(tris, 5)
    assert len(small) > len(tris)
    for t in small:
        for i in range(3):
            a = t[i].position
            b = t[(i + 1) % 3].position
            assert sum((a[k] - b[k]) ** 2 for k in range(3)) ** 0.5 <= 5
    assert abs(_area(small) - _area(tris)) < 1e-6
    ups = [t for t in tris if up_facing(t, 0.9)]
    small_ups = [t for t in small if up_facing(t, 0.9)]
    assert abs(_area(small_ups) - _area(ups)) < 1e-6


def test_inside_follows_the_even_odd_rule() -> None:
    assert inside(SQUARE, 0, 0)
    assert not inside(SQUARE, 11, 0)
    notch = [[0, 0], [10, 0], [10, 10], [5, 2], [0, 10]]
    assert inside(notch, 1, 5)
    assert not inside(notch, 5, 6)


def test_carve_takes_the_triangles_inside_the_outline_and_the_heights() -> None:
    tris = subdivide(_slab(), 4)
    kept, carved = carve(tris, Carve([SQUARE], [-5, 5]))
    assert len(kept) + len(carved) == len(tris)
    for t in carved:
        c = centroid(t)
        assert abs(c[0]) <= 10 and abs(c[2]) <= 10
    for t in kept:
        c = centroid(t)
        assert abs(c[0]) >= 9 or abs(c[2]) >= 9
    # Heights leave out what is above or below them: only the top face (y = 2) here.
    _, top = carve(tris, Carve([SQUARE], [1.5, 5]))
    assert top and all(centroid(t)[1] == 2 for t in top)


def test_chunk_cells_bins_on_the_grid_and_merges_down_to_the_cap() -> None:
    points = [[x + 0.5, 0, z + 0.5] for x in range(4) for z in range(4)]
    assert len(set(chunk_cells(points, 1, 100))) == 16
    ids = chunk_cells(points, 1, 5)
    assert sorted(set(ids)) == [0, 1, 2, 3, 4]
    assert chunk_cells(points, 10, 5) == [0] * 16


def test_shatter_puts_every_triangle_in_exactly_one_chunk_round_its_centre() -> None:
    tris = subdivide(_slab(), 4)
    chunks = shatter(tris, 10, 6)
    assert 1 < len(chunks) <= 6
    assert sum(len(c.tris) for c in chunks) == len(tris)
    for chunk in chunks:
        cs = [centroid(t) for t in chunk.tris]
        mean = [sum(c[a] for c in cs) / len(cs) for a in range(3)]
        assert all(abs(mean[a] - chunk.centre[a]) < 1e-9 for a in range(3))


def test_up_facing_reads_the_babylon_front_normal() -> None:
    tris = _slab()
    tops = [t for t in tris if up_facing(t, 0.9)]
    assert tops and all(centroid(t)[1] == 2 for t in tops)


def test_subdivide_cuts_only_the_triangles_that_need_it() -> None:
    tris = _slab()
    small = subdivide(tris, 5, lambda tri: centroid(tri)[1] > 1.5)
    tops = [t for t in small if centroid(t)[1] == 2]
    others = [t for t in small if centroid(t)[1] != 2]
    assert len(tops) > 2
    assert len(others) == len([t for t in tris if centroid(t)[1] != 2])


def test_a_triangle_straddles_a_region_it_crosses_or_holds_a_corner_of() -> None:
    region = Carve([SQUARE], [-5, 5])
    a, b, c = (Vertex([x, 0, z], [1, 1, 1, 1]) for x, z in [(-5, 0), (15, 0), (5, 5)])
    assert straddles([a, b, c], region)
    inner = [Vertex([x, 0, z], [1, 1, 1, 1]) for x, z in [(-2, -2), (2, -2), (0, 2)]]
    assert not straddles(inner, region)
    far = [Vertex([x, 0, z], [1, 1, 1, 1]) for x, z in [(30, 30), (40, 30), (35, 40)]]
    assert not straddles(far, region)
    # Bigger than the square, round it: no corner inside, but it holds the outline's corners.
    big = [Vertex([x, 0, z], [1, 1, 1, 1]) for x, z in [(-50, -50), (50, -50), (0, 60)]]
    assert straddles(big, region)
