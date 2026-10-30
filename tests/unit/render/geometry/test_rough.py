"""Unit tests of `src/render/geometry/rough.py` (D-212)."""

import math

from render.geometry.rough import Roughness, ball_profile, rough_ball, rough_lathe
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
