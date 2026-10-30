"""Checks of the geometry the view builds (vertices, indices, colours, bounds), in plain Python.

The builders return `ColoredGeometry` (flat lists of positions, indices and RGBA colours) or a
`PropGeometry` wrapping one; these helpers read them without a renderer.
"""

from typing import Any


def check_colored(geo: Any) -> int:
    """Asserts `geo` is a well-formed mesh and returns its vertex count."""
    vertices = len(geo.positions) // 3
    assert len(geo.positions) == 3 * vertices
    assert len(geo.colors) == 4 * vertices
    assert len(geo.indices) % 3 == 0
    assert all(0 <= i < vertices for i in geo.indices)
    assert all(0 <= c <= 1 for c in geo.colors)
    return vertices


def check_prop(prop: Any) -> int:
    """Asserts a `PropGeometry` is well-formed (its structure, and its lights if it has any)."""
    vertices = check_colored(prop.structure)
    if prop.lights is not None:
        check_colored(prop.lights)
    return vertices


def bounds(geo: Any) -> tuple[list[float], list[float]]:
    """The lowest and highest (x, y, z) of the vertices of `geo`."""
    xs = geo.positions[0::3]
    ys = geo.positions[1::3]
    zs = geo.positions[2::3]
    return [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]


def footprint(geo: Any) -> tuple[float, float]:
    """The width (along X) and depth (along Z) of `geo`."""
    low, high = bounds(geo)
    return high[0] - low[0], high[2] - low[2]


def height(geo: Any) -> float:
    """The height of `geo` above the ground (its highest vertex)."""
    return bounds(geo)[1][1]
