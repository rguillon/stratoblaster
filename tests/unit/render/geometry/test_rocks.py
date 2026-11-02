# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/geometry/rocks.py` (GFX-PROP-19)."""

from helpers.geometry_checks import bounds, check_colored

from render.geometry.rocks import rough_chunk
from render.geometry.rough import Roughness
from render.geometry.solids import Placement, SolidBuilder

STONE = [0.6, 0.6, 0.58]


def _chunk(seed: int, sides: int = 6, push: float = 0.2) -> SolidBuilder:
    s = SolidBuilder()
    rough_chunk(s, [2, 3, 1.5], sides, STONE, Roughness(push, 0.1, 0.3, seed), Placement())
    return s


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _triangles(s: SolidBuilder) -> list[list[list[float]]]:
    p = s.geometry.positions
    ix = s.geometry.indices
    return [[p[3 * i : 3 * i + 3] for i in ix[t : t + 3]] for t in range(0, len(ix), 3)]


def test_gfx_prop_19_a_chunk_has_two_bands_of_facets_and_a_top() -> None:
    s = _chunk(1)
    assert check_colored(s.geometry) > 0
    # 6 sides: 2 bands of 6 facets of 2 triangles, a top of 6.
    assert len(s.geometry.indices) // 3 == 2 * 6 * 2 + 6


def test_gfx_prop_19_a_chunk_stands_on_the_ground_about_its_size() -> None:
    low, high = bounds(_chunk(2).geometry)
    assert low[1] == 0
    assert 2.5 < high[1] < 3.6
    assert 1.6 < high[0] - low[0] < 2.6
    assert 1.2 < high[2] - low[2] < 2


def test_gfx_prop_19_the_facets_face_outwards_and_the_top_up() -> None:
    """Babylon front faces have the normal (c - a) x (b - a) (`SolidBuilder.face`)."""
    for tri in _triangles(_chunk(3)):
        a, b, c = tri
        n = _cross([c[k] - a[k] for k in range(3)], [b[k] - a[k] for k in range(3)])
        centre = [(a[k] + b[k] + c[k]) / 3 for k in range(3)]
        # Outwards: away from the axis, or up for the top.
        assert n[0] * centre[0] + n[2] * centre[2] > 0 or n[1] > 0


def test_gfx_prop_19_the_corners_are_pushed_about_so_no_two_chunks_are_the_same() -> None:
    assert _chunk(4).geometry.positions != _chunk(5).geometry.positions
    assert _chunk(4).geometry.positions == _chunk(4).geometry.positions
    xs = _chunk(6).geometry.positions[0::3]
    # A regular hexagon would have 2 corners at x = 1 (the width is 2): pushed, none is.
    assert not any(abs(x - 1) < 1e-9 for x in xs)


def test_gfx_prop_19_the_facets_are_shaded_darker_towards_the_base() -> None:
    geo = _chunk(7).geometry
    ys = geo.positions[1::3]
    reds = geo.colors[0::4]
    low = [r for r, y in zip(reds, ys, strict=True) if y < 0.01]
    high = [r for r, y in zip(reds, ys, strict=True) if y > 2.5]
    assert sum(low) / len(low) < sum(high) / len(high)
    assert len(set(reds)) > 6
