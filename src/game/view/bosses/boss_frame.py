# Copyright (c) 2026 Renaud Guillon
"""The dark metal frame a boss's shed armour leaves (BOSS-44, D-254).

A dark floor in the region's own top-view outline, metal ribs across it (wing, shell or ring), neon
seams on one rib in three and pipes along the two longest. Drawn from the region's outlines, under
the armour's lowest point, unless the boss draws its own.

Model space of a boss: logical pixels, +Y up (towards the camera), see `boss_limbs.boss_point`.
"""

import math

from game.config.boss_look import BOSS_LOOK
from render.geometry.frame_lines import Footprint, clip_line, frame_lines
from render.geometry.outline import reversed_copy, ring_at
from render.geometry.solids import Placement
from render.geometry.triangulate import triangulate_polygon

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


QUARTER = math.pi / 2
# How thick the floor is drawn.
FLOOR = 0.4


def _double_area(ring: list[Any]) -> float:
    total = 0.0
    n = len(ring)
    for i in range(n):
        a = ring[i]
        b = ring[(i + 1) % n]
        total += a[0] * b[1] - b[0] * a[1]
    return total


def footprint_of(outlines: list[Any]) -> Footprint:
    """Return the top view of `outlines` (XZ polygons), triangulated."""
    tris: list[Any] = []
    for outline in outlines:
        ring = list(outline) if _double_area(outline) > 0 else reversed_copy(outline)
        for a, b, c in triangulate_polygon(ring):
            tris.append([ring_at(ring, a), ring_at(ring, b), ring_at(ring, c)])
    return Footprint(tris)


def frame_segments(outlines: list[Any], style: str) -> list[list[Any]]:
    """Return the frame's ribs over `outlines`, each `[a, b]` (XZ), in the `style`."""
    look = BOSS_LOOK.frame
    shape = footprint_of(outlines)
    if shape.empty():
        return []
    result: list[list[Any]] = []
    for line in frame_lines(style, shape, look.ribGap, look.spokes):
        result.extend(clip_line(line, shape, look.step, look.least))
    return result


def _length(segment: list[Any]) -> float:
    return math.hypot(segment[1][0] - segment[0][0], segment[1][1] - segment[0][1])


def longest_two(segments: list[list[Any]]) -> list[list[Any]]:
    """Return the two longest of `segments` (fewer if there are fewer), longest first."""
    result: list[list[Any]] = []
    for segment in segments:
        if len(result) < 2 or _length(segment) > _length(result[1]):
            result.append(segment)
            if len(result) == 2 and _length(result[1]) > _length(result[0]):
                result = [result[1], result[0]]
            elif len(result) == 3:
                if _length(result[2]) > _length(result[0]):
                    result = [result[2], result[0]]
                else:
                    result = [result[0], result[2]]
    return result


def _draw_rib(p: Any, segment: list[Any], y: float, seam: Any) -> None:
    """Draw a rib along `segment` at height `y`, with a neon `seam` on top if given."""
    look = BOSS_LOOK.frame
    a = segment[0]
    b = segment[1]
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    length = math.hypot(dx, dz)
    yaw = math.atan2(dx, dz)
    mid = [(a[0] + b[0]) / 2, y, (a[1] + b[1]) / 2]
    w = look.ribWidth
    h = look.ribHeight
    p.hull.box([w, h, length], look.metal, Placement(mid, yaw))
    if seam != None:
        p.neon.box([w * 0.25, 0.2, length * 0.8], seam, Placement([mid[0], y + h, mid[2]], yaw))


def _draw_pipe(p: Any, segment: list[Any], y: float) -> None:
    """Draw a pipe beside the rib along `segment`, on the floor."""
    look = BOSS_LOOK.frame
    a = segment[0]
    b = segment[1]
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    length = math.hypot(dx, dz)
    w = look.ribWidth
    ox = (dz / length) * w * 1.6
    oz = (-dx / length) * w * 1.6
    r = look.pipeRadius
    place = Placement([a[0] + ox, y + r, a[1] + oz], math.atan2(dx, dz), QUARTER)
    p.hull.cylinder(r, length, 6, look.pipe, place)


def frame_drawings(outlines: list[Any], style: str, neon: Any, floor: float) -> list[Any]:
    """Return the drawings (`draw(p)`) of the frame left in `outlines` (XZ, model space).

    They are `[floor, ribs]` (the floor alone carries the frame's glowing outline): a dark floor
    `FLOOR` thick up to height `floor`, and the ribs of the `style` on it.
    """
    look = BOSS_LOOK.frame
    segments = frame_segments(outlines, style)
    longest = longest_two(segments)

    def draw_floor(p: Any) -> None:
        for outline in outlines:
            p.hull.slab(outline, [floor - FLOOR, floor], look.floor)

    def draw_ribs(p: Any) -> None:
        for i in range(len(segments)):
            _draw_rib(p, segments[i], floor, neon if i % look.seamEvery == 0 else None)
        for segment in longest:
            _draw_pipe(p, segment, floor)

    return [draw_floor, draw_ribs]
