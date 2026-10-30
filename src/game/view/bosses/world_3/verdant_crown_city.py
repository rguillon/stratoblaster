"""P09-R09, 3-5: the Verdant Crown's city round its dome: overgrown towers with lit windows, moss
on their roofs and vines climbing them, moss patches and vines across the deck. Model space: logical
pixels, nose +Z (down the
screen), Y up towards the camera."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.world_3.jungle_flesh import table
from game.view.bosses.world_3.verdant_crown_garden import DECK_TOP, EMERALD, JUNGLE, MAGENTA
from game.view.bosses.world_3.verdant_crown_parts import rect
from game.view.enemies.enemy_shapes import SIDES, decal
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

H = ENEMY_LOOK.hull

# A tower: where (model x, z, right half, mirrored), its footprint and height.
TOWERS = table(
    [
        [22, 66, 9, 8, 12],
        [44, 30, 8, 9, 17],
        [52, -4, 8, 10, 11],
        [40, -68, 9, 8, 15],
        [18, -76, 7, 7, 9],
        [20, -40, 7, 8, 19],
        [56, 20, 6, 6, 8],
    ]
)
# Moss patches on the deck (right half, mirrored): centre, width, length.
MOSS = table(
    [
        [14, 58, 10, 7],
        [36, -18, 8, 6],
        [8, -66, 7, 9],
        [50, 8, 6, 8],
    ]
)
# Vines crawling over the deck, as chains of points (right half, mirrored).
VINES = table(
    [
        [[60, -12], [54, -18], [44, -16], [36, -22]],
        [[4, 40], [12, 46], [18, 40]],
    ]
)
WINDOW = record({"w": 1.4, "h": 1.2, "rows": 4})


def pane(tower: list[float], x: float, y: float) -> Vec3:
    """A point on a tower's front face at `x` across and `y` up (sloping back as it rises)."""
    tz = tower[1]
    td = tower[3]
    th = tower[4]
    return [x, y, tz + td / 2 - (y - DECK_TOP) / th + 0.12]


def windows(p: EnemyParts, tower: list[float], lit: Rgb) -> None:
    """Lit panes down the front of a tower (its front at `tz + td / 2`, sloping back by its chamfer
    of 1 as it rises), a few dark."""
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
            y = DECK_TOP + 2 + r * WINDOW.rows
            p.neon.face(
                [
                    pane(tower, a, y),
                    pane(tower, b, y),
                    pane(tower, b, y + WINDOW.h),
                    pane(tower, a, y + WINDOW.h),
                ],
                lit,
            )


def tower(p: EnemyParts, t: list[float], i: int) -> None:
    """An overgrown tower: a chamfered block, its lit windows, moss on its roof, a vine up its
    side."""
    x = t[0]
    z = t[1]
    w = t[2]
    d = t[3]
    h = t[4]
    top = DECK_TOP + h
    p.hull.bevel_slab(
        rect(w, d, [x, z]),
        [DECK_TOP - 1, DECK_TOP, top],
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
    windows(p, t, EMERALD if i % 2 == 0 else MAGENTA)
    side = 1 if x > 0 else -1
    p.hull.box(
        [0.8, h * 0.8, 1.2],
        JUNGLE["leaf"],
        Placement([x + side * (w / 2 - 0.2), DECK_TOP, z]),
    )


def vine(p: EnemyParts, points: list[OutlinePoint]) -> None:
    """A vine crawling over the deck through `points`, leaves along it."""
    hull = p.hull
    for k in range(len(points) - 1):
        ax = points[k][0]
        az = points[k][1]
        bx = points[k + 1][0]
        bz = points[k + 1][1]
        dx = bx - ax
        dz = bz - az
        at: Vec3 = [ax, DECK_TOP, az]
        hull.box(
            [0.9, 0.7, math.hypot(dx, dz)],
            JUNGLE["leaf"],
            Placement([(ax + bx) / 2, DECK_TOP, (az + bz) / 2], math.atan2(dx, dz)),
        )
        hull.box([2, 0.4, 1.4], JUNGLE["moss"], Placement(at, k))


def draw_city(p: EnemyParts) -> None:
    """The city round the dome (P09-R09): towers, moss and vines, on both sides of the deck."""
    for s in SIDES:
        for i in range(len(TOWERS)):
            t = TOWERS[i]
            tower(p, [s * t[0], t[1], t[2], t[3], t[4]], i + (0 if s > 0 else 1))
        for m in MOSS:
            decal(
                p.hull,
                table(rect(m[2], m[3], [s * m[0], m[1]])),
                DECK_TOP + 0.05,
                JUNGLE["moss"],
            )
        for points in VINES:
            vine(p, [[s * pt[0], pt[1]] for pt in points])
