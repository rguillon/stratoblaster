# Copyright (c) 2026 Renaud Guillon
"""MB-BELL-KEEP-03 to MB-BELL-KEEP-05: the Bell Keep's parts, drawbridges and spire.

Logical pixels, nose +Z, Y up (towards the camera). Its front towers and its bell tower (its
parts), its two drawbridges (moving pieces, BOSS-45: drawn lowered, they rest raised) and the slate
spire over its donjon's rotor (a hatch, BOSS-58). Stone, iron and timber with gold light lines: a
floating castle, not a creature (the Lab's third round, user request 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.bell_keep import (
    BELFRY_HALF,
    BELFRY_TOP,
    BELL_BEAM,
    BELL_FRAME,
    BELL_ROTOR_AT,
    BRIDGE_LENGTH,
    BRIDGE_THICK,
    DONJON_TOP,
    FLOOR,
    GATE,
    GATE_FRONT,
    MERLON,
    ROCK_TOP,
    ROTOR_AT,
    SPIRE_RADIUS,
    TOWER_RADIUS,
    TOWER_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["bell-keep"]
# Its materials' shades: pale dressed stone for its walls, a darker course, timber, slate.
STONE = [0.17, 0.165, 0.155]
COURSE = [0.12, 0.115, 0.11]
TIMBER = [0.11, 0.095, 0.08]
SLATE = [0.075, 0.08, 0.095]


def pt(x: float, y: float) -> list[float]:
    """Return a config point `(x, y)` as a slab outline point (model X, Z)."""
    return [-x, -y]


def merlon_ring(p: Any, at: Vec3, radius: float, top: float, count: int, size: float) -> None:
    """Add `count` merlons round a drum's top, `radius` out from `at` (model), on `top`."""
    for k in range(count):
        a = (k + 0.5) * 2 * math.pi / count
        x = at[0] + math.cos(a) * radius
        z = at[2] + math.sin(a) * radius
        p.flesh.box(
            [size, MERLON, 2.2], STONE, Placement([x, top, z], math.atan2(math.cos(a), math.sin(a)))
        )


def banner(p: Any, pole: Vec3, side: float, length: float) -> None:
    """Add a pole at `pole` (model, its foot) and a pennant streaming from its top, fluttering.

    `side`: the way it streams (+1 to model +X).
    """
    height = 9
    p.hull.cylinder(0.35, height, 4, M.base, Placement(pole))
    top = [pole[0], pole[1] + height - 0.3, pole[2]]
    p.neon.box([0.9, 0.9, 0.9], N, Placement([top[0], top[1], top[2]]))

    def draw(w: Any) -> None:
        s = side
        x0 = top[0]
        w.hull.face(
            [
                [x0, top[1], top[2] - 1.6],
                [x0 + s * length, top[1] - 0.6, top[2] - 0.2],
                [x0 + s * length * 0.7, top[1] - 0.5, top[2]],
                [x0 + s * length, top[1] - 0.6, top[2] + 0.3],
                [x0, top[1], top[2] + 1.6],
            ]
            if s < 0
            else [
                [x0, top[1], top[2] + 1.6],
                [x0 + s * length, top[1] - 0.6, top[2] + 0.3],
                [x0 + s * length * 0.7, top[1] - 0.5, top[2]],
                [x0 + s * length, top[1] - 0.6, top[2] - 0.2],
                [x0, top[1], top[2] - 1.6],
            ],
            COURSE,
        )
        w.neon.box(
            [length * 0.6, 0.15, 0.35], N, Placement([x0 + s * length * 0.35, top[1] - 0.2, top[2]])
        )

    p.flap(top, side, length, draw)


def tower(p: Any, at: Vec3) -> None:
    """Draw a front tower (MB-BELL-KEEP-03): a stone drum, corbelled, crenellated, lit slits.

    Its twin-barrelled turret stands on its top (BOSS-58); a pennant streams from its outer side.
    """
    x = at[0]
    z = at[2]
    r = TOWER_RADIUS
    p.flesh.lathe(
        [
            [r + 0.8, ROCK_TOP],
            [r, ROCK_TOP + 2],
            [r, TOWER_TOP - 4],
            [r + 1.4, TOWER_TOP - 2.5],
            [r + 1.4, TOWER_TOP],
        ],
        10,
        STONE,
        Placement([x, 0, z]),
    )
    p.flesh.ring(r + 0.05, 1.2, 10, COURSE, Placement([x, 12, z]))
    p.neon.ring(r + 1.45, 0.35, 10, N, Placement([x, TOWER_TOP - 1.6, z]))
    merlon_ring(p, [x, 0, z], r + 0.6, TOWER_TOP, 8, 2.4)
    # Its floor round the turret, and lit arrow slits facing out.
    p.hull.cylinder(r - 0.4, 0.4, 10, M.base, Placement([x, TOWER_TOP - 0.3, z]))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        q = [x + math.cos(a) * (r + 0.05), 15, z + math.sin(a) * (r + 0.05)]
        p.neon.box([0.6, 3, 0.6], N, Placement(q, -a))
    side = 1 if x > 0 else -1
    banner(p, [x + side * (r - 1.2), TOWER_TOP, z + 3], side, 9)


def belfry(p: Any, at: Vec3) -> None:
    """Draw the bell tower (MB-BELL-KEEP-04): a square stone tower, its bell frame over its back.

    Merlons at its corners, a lit band and slits, the seat of its bell rotor on its front half, the
    timber frame (four posts, a beam either side, the axle) its bell swings in (`bell_keep_rig`).
    """
    x = at[0]
    z = at[2]
    h = BELFRY_HALF
    outline = [[x - h, z - h], [x + h, z - h], [x + h, z + h], [x - h, z + h]]
    p.flesh.bevel_slab(outline, [ROCK_TOP, BELFRY_TOP - 1.4, BELFRY_TOP], [0, 0.8], STONE)
    p.flesh.box([2 * h + 0.3, 1.4, 2 * h + 0.3], COURSE, Placement([x, 11, z]))
    p.neon.box([2 * h + 0.5, 0.4, 2 * h + 0.5], N, Placement([x, BELFRY_TOP - 3.2, z]))
    for sx in [-1, 1]:
        for sz in [-1, 1]:
            p.flesh.box(
                [3, MERLON + 1, 3],
                STONE,
                Placement([x + sx * (h - 1.5), BELFRY_TOP, z + sz * (h - 1.5)]),
            )
            p.neon.box(
                [0.7, 0.4, 0.7],
                N,
                Placement([x + sx * (h - 1.5), BELFRY_TOP + MERLON + 1, z + sz * (h - 1.5)]),
            )
    # The rotor's seat: an iron ring on the tower's front half.
    seat = boss_point(BELL_ROTOR_AT[0], BELL_ROTOR_AT[1], BELFRY_TOP)
    p.hull.cylinder(5.4, 0.6, 10, M.panel, Placement([seat[0], BELFRY_TOP - 0.2, seat[2]]))
    p.neon.ring(5.5, 0.3, 10, N, Placement([seat[0], BELFRY_TOP + 0.2, seat[2]]))
    # The bell frame: four timber posts, a beam along each side, the axle across.
    f = BELL_FRAME
    for sx in [-1, 1]:
        for y in [f[1], f[2]]:
            q = boss_point(sx * f[0], y, BELFRY_TOP)
            p.hull.box([1.4, BELL_BEAM - BELFRY_TOP, 1.4], TIMBER, Placement(q))
        a = boss_point(sx * f[0], (f[1] + f[2]) / 2, BELL_BEAM - 1.2)
        p.hull.box([1.2, 1.2, f[2] - f[1] + 1.4], TIMBER, Placement(a))
    axle = boss_point(0, (f[1] + f[2]) / 2, BELL_BEAM - 1.4)
    p.hull.box([2 * f[0] + 1.4, 1.0, 1.0], M.base, Placement(axle))
    p.bare.box(
        [2 * f[0] - 1.6, 0.4, f[2] - f[1] - 1.6], M.dark, Placement([axle[0], BELFRY_TOP, axle[2]])
    )
    for sx in [-1, 1]:
        banner(p, [x + sx * (h - 1.5), BELFRY_TOP + MERLON + 1, z + h - 1.5], sx, 8)


def _ribbed_underside(p: Any, x0: float, x1: float, z0: float, z1: float, y: float) -> None:
    """Add ribbed planking under a flat piece (model X `x0..x1`, Z `z0..z1`, its bottom at `y`).

    Ridges along Z, their faces 40° off flat (the models drop faces turned down: these show when the
    piece is raised or swung).
    """
    teeth = max(2, round((x1 - x0) / 2.2))
    step = (x1 - x0) / teeth
    depth = step / 2 * math.tan(40 * math.pi / 180)
    for k in range(teeth):
        a = x0 + k * step
        m = a + step / 2
        b = a + step
        # Two faces per ridge, each turned outward and down.
        p.hull.face([[a, y, z0], [m, y - depth, z0], [m, y - depth, z1], [a, y, z1]], TIMBER)
        p.hull.face([[m, y - depth, z0], [b, y, z0], [b, y, z1], [m, y - depth, z1]], TIMBER)


def drawbridge(side: float) -> Any:
    """Return the drawing of the drawbridge on `side` (+1 the config's right), lowered, as drawn.

    Timber planking on iron bands, a lit edge along its sides, iron shoes at its tip; ribbed
    underneath, so that raised it shows its planks to the front (MB-BELL-KEEP-05).
    """

    def draw(p: Any) -> None:
        a = boss_point(side * GATE[0], GATE_FRONT)
        b = boss_point(side * GATE[1], GATE_FRONT - BRIDGE_LENGTH)
        x0 = min(a[0], b[0])
        x1 = max(a[0], b[0])
        z0 = a[2]
        z1 = b[2]
        top = FLOOR
        p.flesh.slab([[x0, z0], [x1, z0], [x1, z1], [x0, z1]], [top - BRIDGE_THICK, top], TIMBER)
        _ribbed_underside(p, x0, x1, z0 + 0.2, z1 - 0.2, top - BRIDGE_THICK)
        # Plank seams, iron bands across, a lit strip along each side, the tip's iron shoe.
        for k in range(1, 4):
            x = x0 + k * (x1 - x0) / 4
            p.bare.box([0.25, 0.2, z1 - z0 - 0.8], COURSE, Placement([x, top, (z0 + z1) / 2]))
        for f in [0.25, 0.7]:
            z = z0 + f * (z1 - z0)
            p.hull.box([x1 - x0 + 0.3, 0.45, 1.1], M.base, Placement([(x0 + x1) / 2, top - 0.1, z]))
        for x in [x0 + 0.4, x1 - 0.4]:
            p.neon.box([0.4, 0.4, z1 - z0 - 1], N, Placement([x, top, (z0 + z1) / 2]))
        p.hull.box(
            [x1 - x0 + 0.4, BRIDGE_THICK + 0.6, 1.2],
            M.panel,
            Placement([(x0 + x1) / 2, top - BRIDGE_THICK - 0.2, z1 - 0.6]),
        )
        for x in [x0 + 1.2, x1 - 1.2]:
            p.hull.box([1.2, 1, 1.2], M.base, Placement([x, top, z1 - 1.4]))

    return draw


def spire(p: Any) -> None:
    """Draw the slate spire over the donjon's rotor (BOSS-58): it bursts as the rotor comes out.

    An octagonal cone on a stone collar, lit ribs up its edges, a gold finial.
    """
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    r = SPIRE_RADIUS
    p.flesh.lathe(
        [[r + 0.3, DONJON_TOP], [r + 0.3, DONJON_TOP + 1.4]],
        8,
        STONE,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    p.hull.lathe(
        [[r, DONJON_TOP + 1.4], [r * 0.45, DONJON_TOP + 7], [0, DONJON_TOP + 12]],
        8,
        SLATE,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 8
        foot = [at[0] + math.cos(a) * r * 0.92, DONJON_TOP + 1.6, at[2] + math.sin(a) * r * 0.92]
        mid = [at[0] + math.cos(a) * r * 0.42, DONJON_TOP + 7.2, at[2] + math.sin(a) * r * 0.42]
        p.neon.face(
            [foot, mid, [mid[0], mid[1] + 0.4, mid[2]], [foot[0], foot[1] + 0.4, foot[2]]], N
        )
    p.neon.cylinder(0.5, 2.4, 4, N, Placement([at[0], DONJON_TOP + 11.5, at[2]]))


def spire_frame(p: Any) -> None:
    """Draw what the spire leaves (BOSS-44): an iron collar round the well the rotor rises from."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(SPIRE_RADIUS, 1.2, 12, M.base, Placement([at[0], DONJON_TOP - 0.4, at[2]]))
    p.neon.ring(SPIRE_RADIUS, 0.3, 12, N, Placement([at[0], DONJON_TOP + 0.7, at[2]]))
    p.bare.cylinder(
        SPIRE_RADIUS - 0.3, 0.3, 12, M.dark, Placement([at[0], DONJON_TOP - 0.2, at[2]])
    )


def keep_armour() -> Any:
    """Return the Bell Keep's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "bridge-right": {"whole": drawbridge(1)},
        "bridge-left": {"whole": drawbridge(-1)},
        "spire": {"whole": spire, "frame": spire_frame},
    }
