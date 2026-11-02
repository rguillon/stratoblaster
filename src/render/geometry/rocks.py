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

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
Rgb = list[float]
Vec3 = list[float]
__pragma__("noskip")

# Draws of a corner (its push out, its turn round the chunk, its lift), of a half facet (its shade)
# and of the chunk (the tilt of its top): each has its own stream.
_PUSH = 1
_TURN = 2
_LIFT = 3
_SHADE = 4
_TILT = 5
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

    rings = [base, waist, top]
    for k in range(2):
        below = rings[k]
        above = rings[k + 1]
        for i in range(sides):
            j = (i + 1) % sides
            # Outward faces counter-clockwise (as `SolidBuilder.lathe` turns them).
            s.face([below[j], below[i], above[i]], tint(k, i, 0), place)
            s.face([below[j], above[i], above[j]], tint(k, i, 1), place)
    centre: Vec3 = [0, 0, 0]
    for p in top:
        centre = [centre[0] + p[0] / sides, centre[1] + p[1] / sides, centre[2] + p[2] / sides]
    for i in range(sides):
        j = (i + 1) % sides
        lit = shaded(color, TOP_LIGHT * (1 + _draw(rough, 3, i, _SHADE) * rough.shade))
        s.face([centre, top[j], top[i]], lit, place)
