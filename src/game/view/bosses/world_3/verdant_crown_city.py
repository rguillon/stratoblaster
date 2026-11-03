# Copyright (c) 2026 Renaud Guillon
"""FB-VERDANT-CROWN-03, 3-5: the Verdant Crown's city round its dome.

Overgrown towers with lit windows, moss on their roofs and vines climbing them, moss patches and
vines across the deck. Each stands on the deck itself (`CORE`) or on the plating the Crown sheds
(`FLANKS`, `SPINE`; D-254), drawn with it. Model space: logical pixels, nose +Z (down the screen),
Y up towards the camera.
"""

import math

from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.world_3.jungle_flesh import table
from game.view.bosses.world_3.verdant_crown_garden import EMERALD, JUNGLE, MAGENTA
from game.view.bosses.world_3.verdant_crown_parts import rect
from game.view.enemies.enemy_shapes import SIDES, decal
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from game.view.enemies.enemy_mesh import EnemyParts
from render.geometry.outline import OutlinePoint

type Rgb = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull

# What a piece of the city stands on: the deck (the core), the flank plating or the spine plating.
CORE = 0
FLANKS = 1
SPINE = 2
# A tower: where (model x, z, right half, mirrored), its footprint and height, what it stands on.
TOWERS = table([
    [22, 66, 9, 8, 12, CORE],
    [44, 30, 8, 9, 17, FLANKS],
    [52, -4, 8, 10, 11, FLANKS],
    [40, -68, 9, 8, 15, CORE],
    [18, -76, 7, 7, 9, SPINE],
    [20, -40, 7, 8, 19, SPINE],
    [56, 20, 6, 6, 8, FLANKS],
])
# Moss patches on the deck (right half, mirrored): centre, width, length, what they lie on.
MOSS = table([
    [14, 58, 10, 7, CORE],
    [36, -18, 8, 6, FLANKS],
    [8, -66, 7, 9, SPINE],
    [50, 8, 6, 8, FLANKS],
])
# Vines crawling over the deck, as chains of points (right half, mirrored), what they lie on.
VINES = table([
    [[[60, -12], [54, -18], [44, -16], [36, -22]], FLANKS],
    [[[4, 40], [12, 46], [18, 40]], CORE],
])
WINDOW = record({"w": 1.4, "h": 1.2, "rows": 4})


def pane(tower: list[float], x: float, y: float, base: float) -> Vec3:
    """Return a point on a tower's front face at `x` across and `y` up, standing on `base`.

    The face slopes back as it rises.
    """
    tz = tower[1]
    td = tower[3]
    th = tower[4]
    return [x, y, tz + td / 2 - (y - base) / th + 0.12]


def windows(p: EnemyParts, tower: list[float], lit: Rgb, base: float) -> None:
    """Add lit panes down the front of a tower standing on `base`, a few dark.

    Its front is at `tz + td / 2`, sloping back by its chamfer of 1 as it rises.
    """
    tx = tower[0]
    tw = tower[2]
    th = tower[4]
    cols = max(1, math.floor((tw - 2) / 2.4))
    rows = math.floor((th - 2) / WINDOW.rows)
    for r in range(rows):
        for c in range(cols):
            if (r * 5 + c * 3 + math.floor(tx + 0.5)) % 4 == 0:
                continue
            cx = tx + (c - (cols - 1) / 2) * 2.4
            a = cx - WINDOW.w / 2
            b = cx + WINDOW.w / 2
            y = base + 2 + r * WINDOW.rows
            p.neon.face(
                [
                    pane(tower, a, y, base),
                    pane(tower, b, y, base),
                    pane(tower, b, y + WINDOW.h, base),
                    pane(tower, a, y + WINDOW.h, base),
                ],
                lit,
            )


def tower(p: EnemyParts, t: list[float], i: int, base: float) -> None:
    """Add an overgrown tower standing on `base` (the deck, or the plating).

    A chamfered block, its lit windows, moss on its roof, a vine up its side.
    """
    x = t[0]
    z = t[1]
    w = t[2]
    d = t[3]
    h = t[4]
    top = base + h
    p.hull.bevel_slab(
        rect(w, d, [x, z]),
        [base - 1, base, top],
        [0, 1],
        H.panel,
        None,
        H.base,
    )
    p.hull.bevel_slab(
        rect(w - 2.4, d - 2.4, [x, z]),
        [top, top, top + 0.8],
        [0, 0.6],
        JUNGLE["moss"],
    )
    windows(p, t, EMERALD if i % 2 == 0 else MAGENTA, base)
    side = 1 if x > 0 else -1
    p.hull.box(
        [0.8, h * 0.8, 1.2],
        JUNGLE["leaf"],
        Placement([x + side * (w / 2 - 0.2), base, z]),
    )


def vine(p: EnemyParts, points: list[OutlinePoint], base: float) -> None:
    """Add a vine crawling over `base` (the deck or the plating) through `points`, leafed."""
    hull = p.hull
    for k in range(len(points) - 1):
        ax = points[k][0]
        az = points[k][1]
        bx = points[k + 1][0]
        bz = points[k + 1][1]
        dx = bx - ax
        dz = bz - az
        at: Vec3 = [ax, base, az]
        hull.box(
            [0.9, 0.7, math.hypot(dx, dz)],
            JUNGLE["leaf"],
            Placement([(ax + bx) / 2, base, (az + bz) / 2], math.atan2(dx, dz)),
        )
        hull.box([2, 0.4, 1.4], JUNGLE["moss"], Placement(at, k))


def draw_city(p: EnemyParts, on: int, base: float) -> None:
    """Draw the city round the dome (FB-VERDANT-CROWN-03), on both sides of the deck.

    The towers, moss and vines standing `on` the deck (`CORE`) or on a plating (`FLANKS`, `SPINE`),
    at the height `base`.
    """
    for s in SIDES:
        for i in range(len(TOWERS)):
            t = TOWERS[i]
            if t[5] == on:
                tower(p, [s * t[0], t[1], t[2], t[3], t[4]], i + (0 if s > 0 else 1), base)
        for m in MOSS:
            if m[4] == on:
                decal(
                    p.hull,
                    table(rect(m[2], m[3], [s * m[0], m[1]])),
                    base + 0.05,
                    JUNGLE["moss"],
                )
        for entry in VINES:
            if entry[1] == on:
                vine(p, [[s * pt[0], pt[1]] for pt in entry[0]], base)
