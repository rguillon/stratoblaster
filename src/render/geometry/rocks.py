# Copyright (c) 2026 Renaud Guillon
"""Rough chunks of stone (GFX-PROP-19, the cliff blocks).

A chunk is a prism whose corners are pushed about at random: an irregular polygon for its base,
its sides leaning in and bulging at a waist, its top a smaller polygon tilted a little, every half
facet its own shade and darker towards the base. Angular, like a block of fractured rock, and
never twice the same.

Seeded: the same seed gives the same chunk.

Game-agnostic: they draw into a `SolidBuilder` and know nothing of what they are used for.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.noise import hash_2d
from render.geometry.rough import Roughness
from render.geometry.solids import Placement, SolidBuilder, shaded
from render.geometry.vec3 import cross, norm, plus

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
Rgb = list[float]
Vec3 = list[float]
__pragma__("noskip")

# Draws of a corner (its push out, its turn round the chunk, its lift), of a half facet (its
# shade), of the chunk (the tilt of its top) and of the grain of a facet (its bump, the shades of
# its pieces): each has its own stream.
_PUSH = 1
_TURN = 2
_LIFT = 3
_SHADE = 4
_TILT = 5
_GRAIN = 6
# A corner turns round the chunk by up to this share of a side's angle.
TURN = 0.4
# The waist is this much wider than the base, at this share of the height, give or take a sixth.
WAIST = 1.08
WAIST_HEIGHT = 0.5
# The top is this much narrower than the base, and tilted by up to this share of the height.
TOP = 0.86
TILT = 0.2
# The top is this much lighter than the sides: dust and light on it.
TOP_LIGHT = 1.06
# The grain of the stone: each facet triangle is split in three round a point pushed in or out by
# up to this share of the chunk's smaller width, each piece shaded up to this much lighter or
# darker, so a facet is knobbly stone and not one flat plane.
GRAIN_BUMP = 0.05
GRAIN_SHADE = 0.09


def _draw(rough: Roughness, k: int, i: int, stream: int) -> float:
    """Return a draw in [-1, 1) for corner `i` of ring `k` from `stream`."""
    return (hash_2d(k, i, rough.seed * 7 + stream) - 0.5) * 2


def _ring(
    size: Vec3, radius: float, y: float, sides: int, k: int, rough: Roughness, lift: float
) -> list[Vec3]:
    """Return ring `k` of corners at height `y`, `radius` out (half the size is 1), pushed about.

    Each corner is lifted by up to `lift` of the height.
    """
    ring: list[Vec3] = []
    for i in range(sides):
        push = 1 + _draw(rough, k, i, _PUSH) * rough.push
        a = ((i + _draw(rough, k, i, _TURN) * TURN) / sides) * math.pi * 2
        r = radius * push
        dy = _draw(rough, k, i, _LIFT) * lift * size[1]
        ring.append([r * math.cos(a) * size[0], y + dy, r * math.sin(a) * size[2]])
    return ring


def rough_chunk(
    s: SolidBuilder,
    size: Vec3,
    sides: int,
    color: Rgb,
    rough: Roughness,
    place: Placement,
) -> None:
    """Add a chunk of stone of `size` (width, height, depth) standing on Y = 0, centred.

    `sides` corners round it, pushed in and out by `rough.push` of their radius and turned a
    little; its waist bulges, its top is smaller, tilted and faceted. No bottom: it stands on or
    in something.
    """
    height = size[1]
    waist_y = height * (WAIST_HEIGHT + _draw(rough, 0, 0, _LIFT) / 6)
    base = _ring(size, 0.5, 0, sides, 0, rough, 0)
    waist = _ring(size, 0.5 * WAIST, waist_y, sides, 1, rough, rough.push / 2)
    top = _ring(size, 0.5 * TOP, height, sides, 2, rough, rough.push / 3)
    # The top tilts: lifted on one side, lowered on the other.
    tilt = _draw(rough, 0, 0, _TILT) * TILT
    turn = hash_2d(0, 1, rough.seed * 7 + _TILT) * math.pi * 2
    for p in top:
        p[1] = p[1] + tilt * height * (p[0] * math.cos(turn) + p[2] * math.sin(turn)) / size[0]

    def tint(k: int, i: int, half: int) -> Rgb:
        draw = _draw(rough, k * 2 + half, i, _SHADE)
        mid = waist_y / 2 if k == 0 else (waist_y + height) / 2
        up = mid / height
        return shaded(color, (1 - rough.shadow * (1 - up)) * (1 + draw * rough.shade))

    bump = GRAIN_BUMP * min(size[0], size[2])
    rings = [base, waist, top]
    for k in range(2):
        below = rings[k]
        above = rings[k + 1]
        for i in range(sides):
            j = (i + 1) % sides
            # Outward faces counter-clockwise (as `SolidBuilder.lathe` turns them).
            n = k * 2 * sides + i * 2
            _grained(s, [below[j], below[i], above[i]], tint(k, i, 0), rough, n, bump, place)
            _grained(s, [below[j], above[i], above[j]], tint(k, i, 1), rough, n + 1, bump, place)
    centre: Vec3 = [0, 0, 0]
    for p in top:
        centre = [centre[0] + p[0] / sides, centre[1] + p[1] / sides, centre[2] + p[2] / sides]
    for i in range(sides):
        j = (i + 1) % sides
        lit = shaded(color, TOP_LIGHT * (1 + _draw(rough, 3, i, _SHADE) * rough.shade))
        _grained(s, [centre, top[j], top[i]], lit, rough, 4 * sides + i, bump, place)


def _grained(
    s: SolidBuilder,
    tri: list[Vec3],
    color: Rgb,
    rough: Roughness,
    n: int,
    bump: float,
    place: Placement,
) -> None:
    """Add facet triangle `n` (counter-clockwise seen from outside) as three pieces of grain.

    They meet at its middle, pushed in or out along its normal by up to `bump`, each its own
    shade.
    """
    a = tri[0]
    b = tri[1]
    c = tri[2]
    normal = norm(
        cross([b[0] - a[0], b[1] - a[1], b[2] - a[2]], [c[0] - a[0], c[1] - a[1], c[2] - a[2]])
    )
    middle = [(a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3]
    middle = plus(middle, normal, _draw(rough, n, 0, _GRAIN) * bump)
    for piece in range(3):
        p = tri[piece]
        q = tri[(piece + 1) % 3]
        shade = 1 + _draw(rough, n, piece + 1, _GRAIN) * GRAIN_SHADE
        s.face([p, q, middle], shaded(color, shade), place)
