"""P07-R05 (phase 7 review: more detail): small surface details shared by the World 1 final
bosses: plates, vents, rivets, hazard stripes, masts
and lights. Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_shapes import decal  # noqa: E402
from render.geometry.outline import hypot3  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[Any]
type Vec3 = list[Any]
__pragma__("noskip")

H = ENEMY_LOOK.hull


def tone(c: Rgb, k: float) -> Rgb:
    """`color` scaled by `k` (darker below 1, lighter above)."""
    return [c[0] * k, c[1] * k, c[2] * k]


# The hull shades used for details, from the darkest to the palest.
SHADE = {
    "dark": H.dark,
    "base": H.base,
    "mid": tone(H.base, 1.3),
    "panel": H.panel,
    "light": tone(H.panel, 1.35),
    "pale": tone(H.panel, 1.9),
    "scorch": [0.05, 0.04, 0.035],
}


def rect(at: list[Any], size: list[Any], yaw: float = 0) -> list[Any]:
    """A rectangle `[w, d]` big around `[cx, cz]`, turned `yaw` radians (seen from above)."""
    cx = at[0]
    cz = at[1]
    w = size[0]
    d = size[1]
    c = math.cos(yaw)
    s = math.sin(yaw)

    def corner(u: float, v: float) -> list[Any]:
        return [cx + u * c + v * s, cz - u * s + v * c]

    return [
        corner(-w / 2, -d / 2),
        corner(w / 2, -d / 2),
        corner(w / 2, d / 2),
        corner(-w / 2, d / 2),
    ]


def plate(
    builder: Any,
    outline: list[Any],
    y: float,
    color: Rgb,
    thick: float = 0.5,
    place: Any = None,
) -> None:
    """An armour plate a little proud of a flat surface at height `y`: the outline, `thick` thick,
    its top edges chamfered."""
    builder.bevel_slab(
        outline,
        [y - 0.2, y - 0.2, y + thick],
        [0, thick * 0.7],
        color,
        place,
    )


def decals(builder: Any, outlines: list[Any], y: float, color: Rgb) -> None:
    """Flat decals at height `y`: one outline each, all of `color` (2 triangles a quad)."""
    for outline in outlines:
        decal(builder, outline, y, color)


def grille(
    builder: Any,
    at: list[Any],
    size: list[Any],
    counts: list[Any],
    yaw: float = 0,
) -> None:
    """A vent grille at height `y`: a dark frame `[w, d]` around `[cx, cz]` and `count` slats
    across it (along X), turned `yaw`. `counts` is `[count, y]`."""
    w = size[0]
    d = size[1]
    count = counts[0]
    y = counts[1]
    decal(builder, rect(at, [w, d], yaw), y, SHADE["dark"])
    step = d / count
    c = math.cos(yaw)
    s = math.sin(yaw)
    for i in range(count):
        v = -d / 2 + step * (i + 0.5)
        centre = [at[0] + v * s, at[1] + v * c]
        decal(builder, rect(centre, [w * 0.8, step * 0.4], yaw), y + 0.04, SHADE["light"])


def along(a: list[Any], b: list[Any], count: int) -> list[Any]:
    """`count` points evenly spread from `a` to `b`, both ends included."""
    result: list[Any] = []
    for i in range(count):
        t = i / (count - 1) if count > 1 else 0.5
        result.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])
    return result


def studs(
    builder: Any,
    ends: list[Any],
    counts: list[Any],
    y: float,
    color: Rgb,
) -> None:
    """A row of small square studs from `a` to `b` at height `y`: rivets, or lights on `neon`.
    `ends` is `[a, b]` and `counts` is `[count, size]`."""
    for p in along(ends[0], ends[1], counts[0]):
        decal(builder, rect(p, [counts[1], counts[1]], 0.785), y, color)


def hazard(builder: Any, at: list[Any], size: list[Any], count: int, y: float) -> None:
    """Hazard stripes in a band `[w, d]` around `at` (across X) at height `y`: a dark band and
    `count` slanted pale stripes on it."""
    cx = at[0]
    cz = at[1]
    w = size[0]
    d = size[1]
    decal(builder, rect(at, [w, d]), y, SHADE["dark"])
    step = w / (count + 0.5)
    for i in range(count):
        x = cx - w / 2 + step * (i + 0.25)
        stripe: list[Any] = [
            [x, cz - d * 0.4],
            [x + step * 0.5, cz - d * 0.4],
            [x + step * 0.75, cz + d * 0.4],
            [x + step * 0.25, cz + d * 0.4],
        ]
        decal(builder, stripe, y + 0.04, SHADE["pale"])


def rod(
    builder: Any,
    start: Vec3,
    end: Vec3,
    radius: float,
    color: Rgb = SHADE["dark"],
) -> None:
    """A thin rod from `start` to `end`: a mast stay, a cable, a whip antenna."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = hypot3(dx, dy, dz) or 1
    pitch = math.acos(dy / length)
    yaw = math.atan2(dx, dz)
    builder.cylinder(radius, length, 4, color, Placement(start, yaw, pitch))


def mast(parts: Any, at: Vec3, height: float, neon: Rgb) -> None:
    """An antenna mast `height` tall standing at `at`, a neon light on its tip."""
    x = at[0]
    y = at[1]
    z = at[2]
    parts.hull.cylinder(0.7, height, 4, SHADE["dark"], Placement(at), 0.3)
    parts.hull.box([3, 0.4, 0.5], SHADE["panel"], Placement([x, y + height * 0.65, z]))
    parts.neon.box([0.9, 0.9, 0.9], neon, Placement([x, y + height, z]))


def dish(parts: Any, at: Vec3, radius: float, tilt_yaw: list[Any]) -> None:
    """A radar dish `radius` wide on a short post at `at`, tilted `tilt` radians towards `yaw`."""
    x = at[0]
    y = at[1]
    z = at[2]
    tilt = tilt_yaw[0]
    yaw = tilt_yaw[1]
    parts.hull.cylinder(radius * 0.18, radius * 0.7, 4, SHADE["dark"], Placement(at))
    bowl = [
        [radius * 0.2, 0],
        [radius, radius * 0.35],
        [radius * 0.9, radius * 0.42],
        [0, radius * 0.12],
    ]
    top = [x, y + radius * 0.6, z]
    parts.hull.lathe(bowl, 8, SHADE["light"], Placement(top, yaw, tilt))
    rod(
        parts.hull,
        top,
        [x + math.sin(yaw) * radius * 0.25, y + radius * 1.1, z],
        0.25,
    )


def greebles(
    builder: Any,
    at: Vec3,
    boxes: list[Any],
    color: Rgb = SHADE["panel"],
) -> None:
    """Small greeble boxes `[dx, dz, w, h, d]` around `at` (its height is their base): pipes,
    boxes."""
    x = at[0]
    y = at[1]
    z = at[2]
    for i in range(len(boxes)):
        b = boxes[i]
        top = SHADE["light"] if i % 2 == 0 else color
        builder.box(
            [b[2], b[3], b[4]],
            color,
            Placement([x + b[0], y, z + b[1]]),
            top,
        )
