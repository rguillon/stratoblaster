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
