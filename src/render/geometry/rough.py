"""Rough bodies of revolution (D-212): a lathe whose vertices are pushed in and out at random and
whose facets each get a slightly different shade, so a ball reads as a clump of leaves, a cone as a
tier of needles. Seeded: the same seed gives the same shape.

Game-agnostic: they draw into a `SolidBuilder` and know nothing of what they are used for.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.noise import hash_2d
from render.geometry.solids import Placement, SolidBuilder

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
Rgb = list[float]
Vec3 = list[float]
ProfilePoint = list[float]
__pragma__("noskip")

# Draws of a vertex (its push) and of a facet (its shade): each has its own stream.
_PUSH = 1
_SHADE = 2


class Roughness:
    """How rough a body is: vertices pushed in or out by up to `push` of their radius, facets
    shaded up to `shade` lighter or darker, and darker by `shadow` at the bottom of the body than at
    its top (as leaves inside a crown are)."""

    def __init__(self, push: float, shade: float, shadow: float, seed: int) -> None:
        self.push = push
        self.shade = shade
        self.shadow = shadow
        self.seed = seed


def _shaded(color: Rgb, k: float) -> Rgb:
    return [min(1, color[0] * k), min(1, color[1] * k), min(1, color[2] * k)]


def rough_lathe(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    profile: list[ProfilePoint],
    sides: int,
    color: Rgb,
    rough: Roughness,
    place: Placement,
) -> None:
    """A body of revolution around Y (`profile`: `[radius, y]` points from bottom to top; a radius
    of 0 closes it to a point there), each vertex pushed along its ring's radius and each facet
    shaded by `rough`, all of it one triangle per facet half."""
    rows = len(profile)
    low = profile[0][1]
    high = profile[rows - 1][1]
    span = high - low if high != low else 1
    rings: list[list[Vec3]] = []
    for k in range(rows):
        r = profile[k][0]
        y = profile[k][1]
        ring: list[Vec3] = []
        for i in range(sides):
            push = 1 + (hash_2d(k, i, rough.seed * 7 + _PUSH) - 0.5) * 2 * rough.push
            a = (i / sides) * math.pi * 2
            # The points closing the body stay on the axis (one point, whatever the push).
            lift = 0 if r == 0 else (hash_2d(i, k, rough.seed * 7 + _PUSH) - 0.5) * rough.push
            ring.append([r * push * math.cos(a), y + lift * r, r * push * math.sin(a)])
        rings.append(ring)

    def tint(k: int, i: int, half: int) -> Rgb:
        draw = hash_2d(k * 2 + half, i, rough.seed * 7 + _SHADE)
        height = (profile[k][1] + profile[k + 1][1]) / 2
        up = (height - low) / span
        return _shaded(color, (1 - rough.shadow * (1 - up)) * (1 + (draw - 0.5) * 2 * rough.shade))

    for k in range(rows - 1):
        below = rings[k]
        above = rings[k + 1]
        for i in range(sides):
            j = (i + 1) % sides
            # The halves of facet `i` between rings `k` and `k + 1`, outward faces counter-clockwise
            # (as `SolidBuilder.lathe` turns them); a half on a ring closed to a point is left out.
            if profile[k][0] != 0:
                s.face([below[j], below[i], above[i]], tint(k, i, 0), place)
            if profile[k + 1][0] != 0:
                s.face([below[j], above[i], above[j]], tint(k, i, 1), place)


def ball_profile(rings: int) -> list[ProfilePoint]:
    """The profile of a ball of radius 1 centred at 0, `rings` rows of facets from pole to pole."""
    # The poles exactly on the axis (`sin(pi)` is not quite 0), so they close the ball.
    return [
        [0 if k in (0, rings) else math.sin(math.pi * k / rings), -math.cos(math.pi * k / rings)]
        for k in range(rings + 1)
    ]


def rough_ball(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    centre: Vec3,
    radii: Vec3,
    color: Rgb,
    rough: Roughness,
) -> None:
    """A rough ball (an ellipsoid of `radii` across X, up Y and across Z) around `centre`."""
    profile = ball_profile(6)
    # Made with radius 1 on its axis and stretched: the profile's radius by X (Z alike), its
    # height by Y.
    stretched = [[p[0] * radii[0], p[1] * radii[1]] for p in profile]
    rough_lathe(s, stretched, 9, color, rough, Placement(centre))


# A direction this close to up is crossed with Z, not with up, for a tuft's sides.
NEAR_UP = 0.9


class Leaves:
    """How a cloud of leaves looks: `palette` (colours picked at random), `count` tufts of about
    `size` across, laid from the surface down to `depth` of the way in (the deeper, the darker, by
    `inner`; the lower, the darker, by `shadow`), each shaded up to `shade` lighter or darker."""

    def __init__(  # noqa: PLR0913, PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        palette: list[Rgb],
        count: int,
        size: float,
        depth: float,
        inner: float,
        shadow: float,
        shade: float,
    ) -> None:
        self.palette = palette
        self.count = count
        self.size = size
        self.depth = depth
        self.inner = inner
        self.shadow = shadow
        self.shade = shade


def _norm(v: Vec3) -> Vec3:
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if length == 0:
        return [0, 1, 0]
    return [v[0] / length, v[1] / length, v[2] / length]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _plus(a: Vec3, b: Vec3, k: float) -> Vec3:
    return [a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k]


def tuft(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    at: Vec3,
    out: Vec3,
    size: float,
    color: Rgb,
    turn: float,
) -> None:
    """A tuft of leaves at `at`: a little three-sided pyramid `size` across, its tip towards `out`
    (a unit vector), turned `turn` round it; its faces face outwards."""
    side = _norm(_cross(out, [0, 0, 1] if abs(out[1]) > NEAR_UP else [0, 1, 0]))
    other = _cross(out, side)
    base: list[Vec3] = []
    for k in range(3):
        angle = turn + k * math.pi * 2 / 3
        corner = _plus(
            _plus(at, side, math.cos(angle) * size * 0.5), other, math.sin(angle) * size * 0.5
        )
        base.append(_plus(corner, out, -size * 0.15))
    tip = _plus(at, out, size * 0.45)
    for k in range(3):
        a = base[k]
        b = base[(k + 1) % 3]
        # Outward: (b - a) x (tip - a) along `out` (SolidBuilder.face: counter-clockwise from out).
        n = _cross(
            [b[0] - a[0], b[1] - a[1], b[2] - a[2]], [tip[0] - a[0], tip[1] - a[1], tip[2] - a[2]]
        )
        mid = [
            (a[0] + b[0] + tip[0]) / 3 - at[0],
            (a[1] + b[1] + tip[1]) / 3 - at[1],
            (a[2] + b[2] + tip[2]) / 3 - at[2],
        ]
        if n[0] * mid[0] + n[1] * mid[1] + n[2] * mid[2] >= 0:
            s.face([a, b, tip], color)
        else:
            s.face([a, tip, b], color)


def _tuft_color(leaves: Leaves, seed: int, k: int, deep: float, up: float) -> Rgb:
    """The colour of tuft `k`: from the palette, darker the deeper (`deep`, 0 at the surface to 1)
    and the lower (`up`, 0 at the bottom to 1 at the top), jittered."""
    palette = leaves.palette
    pick = math.floor(hash_2d(k, 4, seed) * len(palette))
    pick = len(palette) - 1 if pick >= len(palette) else pick
    jitter = 1 + (hash_2d(k, 5, seed) - 0.5) * 2 * leaves.shade
    k_light = (1 - leaves.inner * deep) * (1 - leaves.shadow * (1 - up)) * jitter
    return _shaded(palette[pick], k_light)


def leaf_cloud(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    centre: Vec3,
    radii: Vec3,
    leaves: Leaves,
    seed: int,
) -> None:
    """A clump of leaves: `leaves.count` tufts in the shell of an ellipsoid of `radii` round
    `centre` (D-212: a crown that reads as leaves, not as one smooth ball)."""
    for k in range(leaves.count):
        # A direction spread evenly over the sphere, and how deep in the shell.
        y = hash_2d(k, 0, seed) * 2 - 1
        a = hash_2d(k, 1, seed) * math.pi * 2
        ring = math.sqrt(max(0, 1 - y * y))
        unit = [ring * math.cos(a), y, ring * math.sin(a)]
        deep = hash_2d(k, 2, seed) * leaves.depth
        reach = 1 - deep
        at = [
            centre[0] + unit[0] * radii[0] * reach,
            centre[1] + unit[1] * radii[1] * reach,
            centre[2] + unit[2] * radii[2] * reach,
        ]
        # Out along the ellipsoid's normal, a little askew.
        out = _norm(
            [
                unit[0] / radii[0] + (hash_2d(k, 7, seed) - 0.5) * 0.6 / radii[0],
                unit[1] / radii[1] + (hash_2d(k, 8, seed) - 0.5) * 0.6 / radii[1],
                unit[2] / radii[2] + (hash_2d(k, 9, seed) - 0.5) * 0.6 / radii[2],
            ]
        )
        size = leaves.size * (0.7 + 0.6 * hash_2d(k, 3, seed))
        color = _tuft_color(leaves, seed, k, deep / max(leaves.depth, 1e-6), (y + 1) / 2)
        tuft(s, at, out, size, color, hash_2d(k, 6, seed) * math.pi * 2)


def leaf_cone(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    base: Vec3,
    size: list[float],
    leaves: Leaves,
    seed: int,
) -> None:
    """A tier of needles: `leaves.count` tufts on and just under a cone of `size` (radius, height)
    standing at `base`, pointing out and a little down (D-212: a pine's)."""
    radius = size[0]
    height = size[1]
    slope = radius / height
    for k in range(leaves.count):
        f = math.sqrt(hash_2d(k, 0, seed))
        # More tufts low on the cone, where it is wider: `f` is the share of the way down.
        up = 1 - f
        a = hash_2d(k, 1, seed) * math.pi * 2
        deep = hash_2d(k, 2, seed) * leaves.depth
        r = radius * f * (1 - deep)
        at = [base[0] + math.cos(a) * r, base[1] + up * height, base[2] + math.sin(a) * r]
        out = _norm([math.cos(a), slope - 0.35 + (hash_2d(k, 7, seed) - 0.5) * 0.5, math.sin(a)])
        tuft_size = leaves.size * (0.7 + 0.6 * hash_2d(k, 3, seed))
        color = _tuft_color(leaves, seed, k, deep / max(leaves.depth, 1e-6), up)
        tuft(s, at, out, tuft_size, color, hash_2d(k, 6, seed) * math.pi * 2)
