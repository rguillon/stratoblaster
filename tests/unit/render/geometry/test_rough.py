"""Unit tests of `src/render/geometry/rough.py` (D-212)."""

import math

from render.geometry.rough import (
    Leaves,
    Roughness,
    ball_profile,
    leaf_cloud,
    leaf_cone,
    rough_ball,
    rough_lathe,
    tuft,
)
from render.geometry.solids import Placement, SolidBuilder

GREEN = [0.3, 0.5, 0.2]


def _ball(seed: int, rough: float = 0.2) -> SolidBuilder:
    s = SolidBuilder()
    rough_ball(s, [0, 5, 0], [2, 1, 2], GREEN, Roughness(rough, 0.1, 0.3, seed))
    return s


def test_d212_the_ball_profile_goes_from_pole_to_pole() -> None:
    profile = ball_profile(4)
    assert len(profile) == 5
    assert abs(profile[0][0]) < 1e-9 and profile[0][1] == -1
    assert abs(profile[4][0]) < 1e-9 and abs(profile[4][1] - 1) < 1e-9
    assert abs(profile[2][0] - 1) < 1e-9


def test_d212_a_rough_ball_is_seeded() -> None:
    assert _ball(3).geometry.positions == _ball(3).geometry.positions
    assert _ball(3).geometry.positions != _ball(4).geometry.positions


def test_d212_a_rough_ball_is_one_triangle_per_facet_half_but_at_the_poles() -> None:
    geo = _ball(1).geometry
    # 6 rows of 9 facets, two halves each, but one half on each pole row.
    triangles = 9 * (2 * 6 - 2)
    assert len(geo.indices) == triangles * 3
    assert len(geo.positions) == triangles * 9


def test_d212_without_roughness_the_ball_keeps_its_radii() -> None:
    geo = _ball(1, 0).geometry
    p = geo.positions
    for v in range(len(p) // 3):
        x = p[v * 3] / 2
        y = p[v * 3 + 1] - 5
        z = p[v * 3 + 2] / 2
        assert abs(math.sqrt(x * x + y * y + z * z) - 1) < 1e-6


def test_d212_the_bottom_of_a_body_is_darker_than_its_top() -> None:
    s = SolidBuilder()
    rough_lathe(
        s, [[1, 0], [1, 1], [1, 2]], 8, GREEN, Roughness(0, 0, 0.5, 1), Placement([0, 0, 0])
    )
    colors = s.geometry.colors
    first = colors[1]
    last = colors[len(colors) - 3]
    assert first < last


def test_d212_rough_facets_face_outwards() -> None:
    s = SolidBuilder()
    rough_lathe(s, [[1, 0], [1, 1]], 8, GREEN, Roughness(0, 0, 0, 1), Placement([0, 0, 0]))
    p = s.geometry.positions
    idx = s.geometry.indices
    for t in range(0, len(idx), 3):
        a, b, c = (idx[t + k] * 3 for k in range(3))
        # Babylon's front face normal: (c - a) x (b - a).
        u = [p[c + i] - p[a + i] for i in range(3)]
        w = [p[b + i] - p[a + i] for i in range(3)]
        n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]
        centre = [(p[a + i] + p[b + i] + p[c + i]) / 3 for i in range(3)]
        assert n[0] * centre[0] + n[2] * centre[2] > 0


def _faces_outward_from(s: SolidBuilder, centre: list[float]) -> float:
    """The share of triangles whose front faces away from `centre`."""
    p = s.geometry.positions
    idx = s.geometry.indices
    out = 0
    for t in range(0, len(idx), 3):
        a, b, c = (idx[t + k] * 3 for k in range(3))
        u = [p[c + i] - p[a + i] for i in range(3)]
        w = [p[b + i] - p[a + i] for i in range(3)]
        n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]
        m = [(p[a + i] + p[b + i] + p[c + i]) / 3 - centre[i] for i in range(3)]
        out += 1 if n[0] * m[0] + n[1] * m[1] + n[2] * m[2] > 0 else 0
    return out / (len(idx) // 3)


def test_d212_a_tuft_is_three_faces_facing_out() -> None:
    s = SolidBuilder()
    tuft(s, [0, 0, 0], [0, 1, 0], 1, GREEN, 0.3)
    assert len(s.geometry.indices) == 9
    p = s.geometry.positions
    tip = max(p[k * 3 + 1] for k in range(len(p) // 3))
    assert abs(tip - 0.45) < 1e-9
    # Seen from above (the way the tip points), every face is a front face.
    assert _faces_outward_from(s, [0, -0.2, 0]) == 1


def _leaves(count: int) -> Leaves:
    return Leaves([GREEN, [0.4, 0.6, 0.3]], count, 0.5, 0.3, 0.4, 0.3, 0.1)


def test_d212_a_leaf_cloud_lays_its_tufts_in_the_shell_facing_out() -> None:
    s = SolidBuilder()
    leaf_cloud(s, [0, 5, 0], [2, 1.5, 2], _leaves(200), 7)
    assert len(s.geometry.indices) == 200 * 9
    p = s.geometry.positions
    for v in range(len(p) // 3):
        x = p[v * 3] / 2
        y = (p[v * 3 + 1] - 5) / 1.5
        z = p[v * 3 + 2] / 2
        # Within the shell, give or take a tuft.
        assert math.sqrt(x * x + y * y + z * z) < 1.3
    assert _faces_outward_from(s, [0, 5, 0]) > 0.8


def test_d212_deeper_tufts_are_darker() -> None:
    s = SolidBuilder()
    leaves = Leaves([GREEN], 300, 0.4, 0.5, 0.8, 0, 0)
    leaf_cloud(s, [0, 0, 0], [2, 2, 2], leaves, 3)
    p = s.geometry.positions
    c = s.geometry.colors
    near: list[float] = []
    far: list[float] = []
    for t in range(len(p) // 9):
        v = t * 3
        r = math.sqrt(p[v * 3] ** 2 + p[v * 3 + 1] ** 2 + p[v * 3 + 2] ** 2)
        (far if r > 1.7 else near).append(c[v * 4 + 1])
    assert sum(far) / len(far) > sum(near) / len(near)


def test_d212_a_leaf_cone_stays_on_its_cone() -> None:
    s = SolidBuilder()
    leaf_cone(s, [0, 2, 0], [2, 4], _leaves(150), 5)
    assert len(s.geometry.indices) == 150 * 9
    p = s.geometry.positions
    ys = [p[v * 3 + 1] for v in range(len(p) // 3)]
    assert min(ys) > 2 - 0.5
    assert max(ys) < 6 + 0.5
