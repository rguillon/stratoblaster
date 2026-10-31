"""Unit tests of `src/render/geometry/branches.py` (D-214)."""

import math

from render.geometry.branches import Branching, across, branch, limb
from render.geometry.solids import SolidBuilder

WOOD = [0.6, 0.55, 0.5]
FORKING = Branching(3, 0.7, 0.7, 0.85, 0.3, 0.1, 0.6, 0.1)


def _dot(a: list[float], b: list[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _triangles(s: SolidBuilder) -> int:
    return len(s.geometry.indices) // 3


def _tree(seed: int, depth: int = 2) -> SolidBuilder:
    s = SolidBuilder()
    branch(s, [0, 0, 0], [0, 1, 0], [3, 0.4], depth, FORKING, WOOD, seed)
    return s


def test_d214_across_gives_two_unit_vectors_square_to_the_direction() -> None:
    for d in [[0, 1, 0], [1, 0.2, -0.3], [0, -1, 0.01]]:
        u, v = across(d)
        assert abs(_dot(u, u) - 1) < 1e-9 and abs(_dot(v, v) - 1) < 1e-9
        assert abs(_dot(u, d)) < 1e-9 and abs(_dot(v, d)) < 1e-9 and abs(_dot(u, v)) < 1e-9


def test_d214_a_limb_is_a_capped_prism_or_a_pyramid_open_at_its_start() -> None:
    capped = SolidBuilder()
    limb(capped, [0, 0, 0], [0, 2, 0], [0.5, 0.3], 5, WOOD)
    # 5 quads of 2 triangles, a pentagon cap of 3.
    assert _triangles(capped) == 5 * 2 + 3
    pointed = SolidBuilder()
    limb(pointed, [0, 0, 0], [0, 2, 0], [0.5, 0], 4, WOOD)
    assert _triangles(pointed) == 4


def test_d214_a_limb_faces_outward() -> None:
    s = SolidBuilder()
    limb(s, [1, 1, 1], [3, 2, 1], [0.5, 0.2], 6, WOOD)
    p = s.geometry.positions
    axis = [2, 1, 0]
    for t in range(len(s.geometry.indices) // 3):
        # Babylon's winding: the corners are a, c, b (see `SolidBuilder.face`).
        ia, ib, ic = s.geometry.indices[t * 3 : t * 3 + 3]
        a, b, c = (p[k * 3 : k * 3 + 3] for k in (ia, ic, ib))
        e1 = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
        e2 = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]
        n = [
            e1[1] * e2[2] - e1[2] * e2[1],
            e1[2] * e2[0] - e1[0] * e2[2],
            e1[0] * e2[1] - e1[1] * e2[0],
        ]
        middle = [(a[k] + b[k] + c[k]) / 3 - [1, 1, 1][k] for k in range(3)]
        along = _dot(middle, axis) / _dot(axis, axis)
        out = [middle[k] - axis[k] * along for k in range(3)]
        # The side faces point away from the axis, the cap along it.
        assert _dot(n, out) > 1e-9 or _dot(n, axis) > 1e-9


def test_d214_branches_are_seeded() -> None:
    assert _tree(3).geometry.positions == _tree(3).geometry.positions
    assert _tree(3).geometry.positions != _tree(4).geometry.positions


def test_d214_each_fork_adds_its_limbs() -> None:
    def limbs(depth: int) -> int:
        return sum(FORKING.forks**k for k in range(depth + 1))

    assert limbs(2) == 13
    assert _triangles(_tree(1, 0)) < _triangles(_tree(1, 1)) < _triangles(_tree(1, 2))


def test_d214_a_shallower_branching_is_the_outline_of_a_deeper_one() -> None:
    deep = _tree(5, 2).geometry.positions
    outline = _tree(5, 1).geometry.positions
    # The trunk is the same, and its limbs start where they do in the deeper tree.
    one = SolidBuilder()
    limb(one, [0, 0, 0], [0, 3, 0], [0.4, 0.4 * FORKING.taper], 5, WOOD)
    trunk = len(one.geometry.positions)
    assert outline[:trunk] == deep[:trunk] == one.geometry.positions
    assert outline[trunk : trunk + 3] == deep[trunk : trunk + 3]


def test_d214_limbs_reach_up_and_out_and_thin_out() -> None:
    s = _tree(2, 2)
    xs = s.geometry.positions[0::3]
    ys = s.geometry.positions[1::3]
    assert max(ys) > 4
    assert max(abs(x) for x in xs) > 1
    assert all(not math.isnan(v) for v in s.geometry.positions)
