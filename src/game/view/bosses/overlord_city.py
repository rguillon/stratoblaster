"""P07-R05: the Overlord's city: shared shapes, towers
standing on its deck with lit windows and rooftop clutter, neon edges. Model space: logical pixels,
nose +Z (down the screen), Y up towards the camera; +X is the screen's left.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_shapes import decal, flip_x  # noqa: E402
from game.view.enemies.organic_parts import opt  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[Any]
type Vec3 = list[Any]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
# Purple: the boss's neon (GD-61).
OVERLORD_NEON = BOSS_LOOK.neon["overlord"]
# Heights of the deck's top and of the raised boulevard along its middle.
OVERLORD_DECK = {"top": 6, "boulevard": 10}


def box2d(w: float, d: float, at: Any = None) -> list[Any]:
    """A rectangle `w` wide and `d` long around (x, z)."""
    x = 0 if at == None else at[0]  # noqa: E711
    z = 0 if at == None else at[1]  # noqa: E711
    return [
        [x - w / 2, z - d / 2],
        [x + w / 2, z - d / 2],
        [x + w / 2, z + d / 2],
        [x - w / 2, z + d / 2],
    ]


def symmetric(half: list[Any], nose: Any = None) -> list[Any]:
    """A symmetric outline from its right half (x > 0, from the front to the tail), closed across
    the nose at `nose` on the axis."""
    result: list[Any] = []
    if nose != None:  # noqa: E711
        result.append([0, nose])
    result.extend(half)
    mirror = flip_x(half)
    for i in range(len(mirror) - 1, -1, -1):
        result.append(mirror[i])
    return result


def _area(outline: list[Any]) -> float:
    """Twice the signed area of an outline in (x, z)."""
    total = 0.0
    n = len(outline)
    for i in range(n):
        p = outline[i]
        q = outline[(i + 1) % n]
        total = total + p[0] * q[1] - q[0] * p[1]
    return total


def _lifted(p: Any, y: float, nx: float, nz: float) -> Vec3:
    """The point `p` at height `y`, moved by `[nx, nz]`."""
    return [p[0] + nx, y, p[1] + nz]


def edge_lights(
    neon: Any,
    outline: list[Any],
    edges: list[int],
    heights: list[Any],
    color: Rgb,
    lift: float = 0.35,
) -> None:
    """Neon walls along the edges `edges` of `outline` (edge i from point i to the next), from
    `heights[0]` to `heights[1]`, stood `lift` outside the outline: lit edges with nothing hidden
    inside the hull."""
    y0 = heights[0]
    y1 = heights[1]
    area = _area(outline)
    # Counter-clockwise in (x, z), the outside is on the right of each edge, (dz, -dx).
    out = 1 if area > 0 else -1
    n = len(outline)
    for i in edges:
        p = outline[i]
        q = outline[(i + 1) % n]
        px = p[0]
        pz = p[1]
        qx = q[0]
        qz = q[1]
        length = math.hypot(qx - px, qz - pz) or 1
        nx = (out * lift * (qz - pz)) / length
        nz = (-out * lift * (qx - px)) / length
        if out > 0:
            a = [px, pz]
            b = [qx, qz]
        else:
            a = [qx, qz]
            b = [px, pz]
        neon.face(
            [
                _lifted(a, y0, nx, nz),
                _lifted(a, y1, nx, nz),
                _lifted(b, y1, nx, nz),
                _lifted(b, y0, nx, nz),
            ],
            color,
        )


# How far the towers' tops are inset (their chamfer).
TOWER_INSET = 1.2
WINDOW = {"w": 1.3, "h": 1.1, "rows": 4.2}


def _pane(cx: float, dx: float, y: float, base: float, h: float, front: float) -> Vec3:
    """A point of a window's pane, sloping back with the front of its block."""
    t = (y - base) / h
    return [cx + dx, y, front - TOWER_INSET * t + 0.12]


def _front_windows(neon: Any, at: Vec3, w: float, h: float) -> None:
    """Lit windows on the front of a block `w` wide standing at (x, base, z + d / 2), `h` high,
    its front sloping back by the inset as it rises: a grid of panes, a few dark."""
    x = at[0]
    base = at[1]
    front = at[2]
    cols = max(1, math.floor((w - 2) / 2.2))
    rows = math.floor((h - 1) / WINDOW["rows"])
    for r in range(rows):
        for c in range(cols):
            if (r * 7 + c * 3 + math.floor(x + 0.5)) % 5 == 0:
                continue
            cx = x + (c - (cols - 1) / 2) * 2.2
            y0 = base + 2 + r * WINDOW["rows"]
            a = -WINDOW["w"] / 2
            b = WINDOW["w"] / 2
            corners = [
                _pane(cx, a, y0, base, h, front),
                _pane(cx, b, y0, base, h, front),
                _pane(cx, b, y0 + WINDOW["h"], base, h, front),
                _pane(cx, a, y0 + WINDOW["h"], base, h, front),
            ]
            neon.face(corners, OVERLORD_NEON)


def _draw_roof(parts: Any, roof: str, at: Vec3) -> None:
    """The clutter on a roof at height `y` around (x, z)."""
    hull = parts.hull
    neon = parts.neon
    charge = parts.charge
    x = at[0]
    y = at[1]
    z = at[2]
    if roof == "ac":
        hull.box([2.2, 1.2, 2], H.base, Placement([x - 1.4, y, z - 0.6]), H.panel)
        hull.box([1.6, 1, 1.6], H.base, Placement([x + 1.5, y, z + 0.4]), H.panel)
        decal(hull, box2d(1.4, 1.2, [x - 1.4, z - 0.6]), y + 1.25, H.dark)
    elif roof == "tank":
        hull.cylinder(1.8, 2.6, 6, H.panel, Placement([x, y, z]), 1.5)
        neon.ring(1.85, 0.4, 6, OVERLORD_NEON, Placement([x, y + 1.2, z]))
    else:
        hull.cylinder(0.7, 10, 4, H.dark, Placement([x, y, z]), 0.25)
        charge.box([1.1, 1.1, 1.1], WHITE, Placement([x, y + 9.6, z]))


def draw_tower(parts: Any, tower: Any) -> None:
    """A tower: a chamfered block, lit windows on its front, a lit roof edge, a tier and its roof.
    `tower` is a `Tower`: `x`, `z`, `w`, `d`, `h`, and optionally `tier` and `roof`."""
    hull = parts.hull
    neon = parts.neon
    x = tower.x
    z = tower.z
    w = tower.w
    d = tower.d
    h = tower.h
    tier = opt(tower, "tier", None)
    roof = opt(tower, "roof", None)
    base = OVERLORD_DECK["top"]
    hull.bevel_slab(
        box2d(w, d, [x, z]),
        [base - 1, base, base + h],
        [0, TOWER_INSET],
        H.panel,
        None,
        H.base,
    )
    _front_windows(neon, [x, base, z + d / 2], w, h)
    top = base + h
    if tier != None:  # noqa: E711
        tw = tier[0]
        td = tier[1]
        th = tier[2]
        hull.bevel_slab(
            box2d(tw, td, [x, z - 0.5]),
            [top, top, top + th],
            [0, 0.8],
            H.base,
            None,
            H.panel,
        )
        _front_windows(neon, [x, top, z - 0.5 + td / 2], tw, th)
        top += th
    else:
        decal(
            neon,
            box2d(w - 2 * TOWER_INSET - 1, 0.8, [x, z + d / 2 - 2]),
            top + 0.05,
            OVERLORD_NEON,
        )
    if roof != None:  # noqa: E711
        _draw_roof(parts, roof, [x, top, z - 0.5])
