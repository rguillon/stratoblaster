"""The dark metal frame a boss's shed armour leaves (docs/superpowers/specs/2026-10-31-boss-armour-
shedding-design.md): a dark floor in the armour's own top-view shape, metal ribs across it (wing,
shell or ring), neon seams on every other rib and pipes along the longest (BOSS-44). Its pylons
and bridges hold pieces up so the boss stays one object (BOSS-52).

Model space of a boss: logical pixels, +Y up (towards the camera), see `boss_limbs.boss_point`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from render.geometry.frame_lines import Footprint, clip_line, frame_lines
from render.geometry.shatter import Vertex, append_triangles, up_facing
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

QUARTER = math.pi / 2
# How steep a face of the armour may be and still count in its top view (unit normal Y).
UP = 0.3


def floor_height(tris: list[list[Vertex]]) -> float:
    """The height of the frame's floor under armour made of `tris`: just over its lowest point."""
    low = math.inf
    for tri in tris:
        for v in tri:
            low = min(low, v.position[1])
    lift: float = BOSS_LOOK.frame.lift
    return (low if low < math.inf else 0) + lift


def floor_triangles(tris: list[list[Vertex]], y: float) -> list[list[Vertex]]:
    """The up-facing faces of `tris` laid flat at height `y`, in the frame's floor colour."""
    c = BOSS_LOOK.frame.floor
    color = [c[0], c[1], c[2], 1]
    result: list[list[Vertex]] = []
    for tri in tris:
        if up_facing(tri, UP):
            result.append([Vertex([v.position[0], y, v.position[2]], color) for v in tri])
    return result


def frame_segments(tris: list[list[Vertex]], style: str) -> list[list[Any]]:
    """The frame's ribs over the top view of `tris`, each `[a, b]` (XZ), in the `style`."""
    look = BOSS_LOOK.frame
    shape = Footprint(
        [[[v.position[0], v.position[2]] for v in tri] for tri in tris if up_facing(tri, UP)]
    )
    if shape.empty():
        return []
    result: list[list[Any]] = []
    for line in frame_lines(style, shape, look.ribGap, look.spokes):
        result.extend(clip_line(line, shape, look.step, look.least))
    return result


def _length(segment: list[Any]) -> float:
    return math.hypot(segment[1][0] - segment[0][0], segment[1][1] - segment[0][1])


def longest_two(segments: list[list[Any]]) -> list[list[Any]]:
    """The two longest of `segments` (fewer if there are fewer), longest first."""
    result: list[list[Any]] = []
    for segment in segments:
        if len(result) < 2 or _length(segment) > _length(result[1]):  # noqa: PLR2004
            result.append(segment)
            if len(result) == 2 and _length(result[1]) > _length(result[0]):  # noqa: PLR2004
                result = [result[1], result[0]]
            elif len(result) == 3:  # noqa: PLR2004
                if _length(result[2]) > _length(result[0]):
                    result = [result[2], result[0]]
                else:
                    result = [result[0], result[2]]
    return result


def draw_pylon(p: Any, floor: float, support: list[float], neon: Any) -> None:
    """A pylon up to the base of a piece standing over the frame (`support`: `[x, z, height,
    width]`, and the height it stands on when known, else the frame's `floor`), so it does not
    hover (D-227): a base plate, a column, a collar and a neon band."""
    look = BOSS_LOOK.frame
    x = support[0]
    z = support[1]
    if len(support) > 4:  # noqa: PLR2004
        floor = support[4]
    height = support[2] - floor
    if height <= look.lift:
        return
    w = min(look.pylonMost, max(look.pylonLeast, support[3] * look.pylonShare))
    p.hull.box([w * 1.8, 0.6, w * 1.8], look.metal, Placement([x, floor, z]))
    p.hull.box([w, height, w], look.metal, Placement([x, floor, z]))
    p.hull.box([w * 1.4, 0.8, w * 1.4], look.pipe, Placement([x, floor + height - 0.8, z]))
    p.neon.box([w * 1.05, 0.3, w * 1.05], neon, Placement([x, floor + height * 0.5, z]))


def draw_bridge(p: Any, bridge: list[Any], neon: Any) -> None:
    """A beam holding a patch of frame to the boss (D-227), `[from, to]`: along the floor from
    `from` to under `to`, then a post up (or down) to `to`, a neon seam along the beam."""
    look = BOSS_LOOK.frame
    a = bridge[0]
    b = bridge[1]
    w = look.ribWidth * 1.5
    dx = b[0] - a[0]
    dz = b[2] - a[2]
    length = math.hypot(dx, dz)
    yaw = math.atan2(dx, dz)
    if length > 0:
        mid = [(a[0] + b[0]) / 2, a[1], (a[2] + b[2]) / 2]
        p.hull.box([w, look.ribHeight, length + w], look.metal, Placement(mid, yaw))
        p.neon.box(
            [w * 0.3, 0.2, length * 0.8],
            neon,
            Placement([mid[0], a[1] + look.ribHeight, mid[2]], yaw),
        )
    low = min(a[1], b[1])
    high = max(a[1], b[1])
    p.hull.box([w, high - low + look.ribHeight, w], look.metal, Placement([b[0], low, b[2]]))


def frame_drawings(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    tris: list[list[Vertex]],
    style: str,
    neon: Any,
    supports: list[Any] | None = None,
    floor: Any = None,
    bridges: list[Any] | None = None,
) -> list[Any]:
    """The drawings (`draw(p)`) of the frame left where the armour `tris` was: `[floor, ribs]`
    (the floor alone carries the frame's glowing outline), at height `floor` (else just over the
    armour's lowest point); the ribs hold up the pieces standing over it (`supports`, see
    `draw_pylon`) and beams hold its patches to the boss (`bridges`, see `draw_bridge`)."""
    held = supports if supports is not None else []
    beams = bridges if bridges is not None else []
    look = BOSS_LOOK.frame
    y = floor if floor != None else floor_height(tris)  # noqa: E711
    floor = floor_triangles(tris, y)
    segments = frame_segments(tris, style)
    longest = longest_two(segments)

    def draw_floor(p: Any) -> None:
        append_triangles(p.hull.geometry, floor)

    def draw_ribs(p: Any) -> None:
        w = look.ribWidth
        h = look.ribHeight
        for i in range(len(segments)):
            a = segments[i][0]
            b = segments[i][1]
            dx = b[0] - a[0]
            dz = b[1] - a[1]
            length = math.hypot(dx, dz)
            yaw = math.atan2(dx, dz)
            mid = [(a[0] + b[0]) / 2, y, (a[1] + b[1]) / 2]
            p.hull.box([w, h, length], look.metal, Placement(mid, yaw))
            if i % look.seamEvery == 0:
                p.neon.box(
                    [w * 0.25, 0.2, length * 0.8], neon, Placement([mid[0], y + h, mid[2]], yaw)
                )
        for segment in longest:
            a = segment[0]
            b = segment[1]
            dx = b[0] - a[0]
            dz = b[1] - a[1]
            length = math.hypot(dx, dz)
            # Beside the rib, on the floor.
            ox = (dz / length) * w * 1.6
            oz = (-dx / length) * w * 1.6
            r = look.pipeRadius
            place = Placement([a[0] + ox, y + r, a[1] + oz], math.atan2(dx, dz), QUARTER)
            p.hull.cylinder(r, length, 6, look.pipe, place)
        for support in held:
            draw_pylon(p, y, support, neon)
        for bridge in beams:
            draw_bridge(p, bridge, neon)

    return [draw_floor, draw_ribs]
