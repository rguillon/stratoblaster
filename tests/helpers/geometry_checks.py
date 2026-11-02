# Copyright (c) 2026 Renaud Guillon
"""Checks of the geometry the view builds (vertices, indices, colours, bounds), in plain Python.

The builders return `ColoredGeometry` (flat lists of positions, indices and RGBA colours) or a
`PropGeometry` wrapping one; these helpers read them without a renderer.
"""

from typing import Any


def check_colored(geo: Any) -> int:
    """Assert `geo` is a well-formed mesh and return its vertex count."""
    vertices = len(geo.positions) // 3
    assert len(geo.positions) == 3 * vertices
    assert len(geo.colors) == 4 * vertices
    assert len(geo.indices) % 3 == 0
    assert all(0 <= i < vertices for i in geo.indices)
    assert all(0 <= c <= 1 for c in geo.colors)
    return vertices


def check_prop(prop: Any) -> int:
    """Assert a `PropGeometry` is well-formed (its structure, and its lights if it has any)."""
    vertices = check_colored(prop.structure)
    if prop.lights is not None:
        check_colored(prop.lights)
    return vertices


def bounds(geo: Any) -> tuple[list[float], list[float]]:
    """Return the lowest and highest (x, y, z) of the vertices of `geo`."""
    xs = geo.positions[0::3]
    ys = geo.positions[1::3]
    zs = geo.positions[2::3]
    return [min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]


def footprint(geo: Any) -> tuple[float, float]:
    """Return the width (along X) and depth (along Z) of `geo`."""
    low, high = bounds(geo)
    return high[0] - low[0], high[2] - low[2]


def height(geo: Any) -> float:
    """Return the height of `geo` above the ground (its highest vertex)."""
    return bounds(geo)[1][1]


# The checks above as values: a test asserts once, `assert colored_problems(geo) == []`, and reads
# the vertex count with `vertex_count`.


def vertex_count(geo: Any) -> int:
    """Return the number of vertices of `geo` (three positions each)."""
    return len(geo.positions) // 3


def colored_problems(geo: Any) -> list[str]:
    """Return what makes `geo` an ill-formed mesh (see `check_colored`); empty if none."""
    vertices = vertex_count(geo)
    problems: list[str] = []
    if len(geo.positions) != 3 * vertices:
        problems.append(f"{len(geo.positions)} positions is not a multiple of 3")
    if len(geo.colors) != 4 * vertices:
        problems.append(f"{len(geo.colors)} colour values for {vertices} vertices")
    if len(geo.indices) % 3 != 0:
        problems.append(f"{len(geo.indices)} indices is not a multiple of 3")
    if any(not 0 <= i < vertices for i in geo.indices):
        problems.append("an index is out of range")
    if any(not 0 <= c <= 1 for c in geo.colors):
        problems.append("a colour value is outside [0, 1]")
    return problems


def prop_problems(prop: Any) -> list[str]:
    """Return what makes a `PropGeometry` ill formed (see `check_prop`); empty if none."""
    problems = ["structure: " + p for p in colored_problems(prop.structure)]
    if prop.lights is not None:
        problems.extend("lights: " + p for p in colored_problems(prop.lights))
    return problems
