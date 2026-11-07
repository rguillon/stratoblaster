# Copyright (c) 2026 Renaud Guillon
"""FB-CLOUD-DREADNOUGHT-03, FB-CLOUD-DREADNOUGHT-05: the Cloud Dreadnought's parts and armour.

Logical pixels, nose +Z, Y up (towards the camera). Its main turrets' armoured collars, its bridge
(a conning tower and its mast), its lift engines (a ducted fan out on a pylon), its armour belts
(moving pieces, BOSS-45: drawn swung out flat like wings, they rest hanging down its flanks), the
plating of its after deck and the hatch over its stern rotor. A warship, not a creature (the Lab's
third round, user request 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.cloud_dreadnought import (
    BARBETTE_RADIUS,
    BARBETTE_TOP,
    BATTERY_AT,
    BELT,
    BELT_THICK,
    CONNING,
    DECK,
    ENGINE_AT,
    ENGINE_GUN_AT,
    ENGINE_RADIUS,
    PLATING,
    PLATING_TOP,
    ROTOR_AT,
    SUPERSTRUCTURE,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import rod
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["cloud-dreadnought"]
# Its paint: a battleship grey a shade lighter than the dark metal, and its deck's planking.
GREY = [0.15, 0.155, 0.17]
DECKING = [0.11, 0.105, 0.1]


def pt(x: float, y: float) -> list[float]:
    """Return a config point `(x, y)` as a slab outline point (model X, Z)."""
    return [-x, -y]


def main_turret(p: Any, at: Vec3) -> None:
    """Draw a main turret's armour (FB-CLOUD-DREADNOUGHT-03): a heavy collar on its barbette.

    Its triple-barrelled gun (BOSS-58) turns inside it; lit range marks round its rim.
    """
    x = at[0]
    z = at[2]
    r = BARBETTE_RADIUS
    p.hull.lathe(
        [[r + 0.6, BARBETTE_TOP - 2.4], [r + 1.2, BARBETTE_TOP - 1], [r - 0.4, BARBETTE_TOP + 0.8]],
        12,
        GREY,
        Placement([x, 0, z], math.pi / 12),
    )
    p.neon.ring(r + 1.25, 0.35, 12, N, Placement([x, BARBETTE_TOP - 1.2, z], math.pi / 12))
    for k in range(6):
        a = k * math.pi / 3
        q = [x + math.cos(a) * (r + 0.2), BARBETTE_TOP - 0.2, z + math.sin(a) * (r + 0.2)]
        p.hull.box([1.6, 1.4, 1.2], M.base, Placement(q, -a))


def bridge(p: Any, _at: Vec3) -> None:
    """Draw the bridge (FB-CLOUD-DREADNOUGHT-03): a conning tower, its windows lit, and its mast.

    A rangefinder across its roof and a lattice mast behind it with a yard and a lamp; its flak
    rotor stands on the upper tier behind it (BOSS-58).
    """
    c = CONNING
    base = SUPERSTRUCTURE[1][3]
    outline = [pt(c[0], c[1]), pt(-c[0], c[1]), pt(-c[0] + 1.5, c[2]), pt(c[0] - 1.5, c[2])]
    p.hull.bevel_slab(outline, [base, c[3] - 1.2, c[3]], [0, 0.7], GREY, None, M.panel)
    # Its windows round its front and sides: a lit band.
    front = boss_point(0, c[1] - 0.05, c[3] - 3)
    p.neon.box([2 * c[0] - 0.8, 0.9, 0.3], N, Placement(front))
    for s in [-1, 1]:
        q = boss_point(s * (c[0] - 0.4), (c[1] + c[2]) / 2, c[3] - 3)
        p.neon.box([0.3, 0.9, c[2] - c[1] - 2], N, Placement(q))
    # The rangefinder across its roof.
    rf = boss_point(0, c[1] + 3, c[3])
    p.hull.box([2 * c[0] + 6, 1.4, 1.6], M.base, Placement(rf))
    for s in [-1, 1]:
        p.hull.cylinder(1, 1.6, 6, M.panel, Placement([rf[0] + s * (c[0] + 3), c[3], rf[2]]))
        p.neon.box([0.4, 0.4, 0.4], N, Placement([rf[0] + s * (c[0] + 3), c[3] + 1.6, rf[2]]))
    # The mast: a tripod up from its roof's back, a yard across, a lamp on top.
    foot = boss_point(0, c[2] - 1.5, c[3])
    top = [foot[0], c[3] + 9, foot[2] + 1.5]
    for dx in [-2, 2]:
        rod(p.hull, [foot[0] + dx, c[3], foot[2]], top, 0.45, M.base)
    rod(p.hull, [foot[0], c[3], foot[2] - 2.5], top, 0.45, M.base)
    p.hull.box([9, 0.5, 0.5], M.base, Placement([top[0], top[1] - 2.5, top[2]]))
    p.neon.cylinder(0.6, 1.2, 6, N, Placement(top))


def engine(p: Any, at: Vec3) -> None:
    """Draw a lift engine (FB-CLOUD-DREADNOUGHT-03): a ducted fan out on a pylon from the deck.

    The duct's lit rim round its turning fan (a rotor), its fairing and exhaust vanes, the pylon
    from the deck's edge carrying its twin AA turret at its root (BOSS-58).
    """
    s = 1 if at[0] < 0 else -1
    duct = boss_point(s * ENGINE_AT[0], ENGINE_AT[1], 0)
    r = ENGINE_RADIUS
    p.hull.lathe(
        [[r - 1.8, DECK - 4.5], [r + 0.4, DECK - 3.5], [r + 0.6, DECK - 0.8], [r - 0.4, DECK]],
        14,
        GREY,
        Placement([duct[0], 0, duct[2]]),
        False,
    )
    p.hull.lathe(
        [[r - 0.6, DECK], [r - 1.8, DECK - 4.5]],
        14,
        M.base,
        Placement([duct[0], 0, duct[2]]),
        False,
    )
    p.neon.ring(r - 0.2, 0.35, 14, N, Placement([duct[0], DECK + 0.05, duct[2]]))
    p.bare.cylinder(1.8, DECK - 4, 8, M.panel, Placement([duct[0], 0, duct[2]]))
    p.rotor([duct[0], DECK - 2.2, duct[2]], r - 1.4)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        p.bare.box([r * 2 - 4, 0.5, 0.8], M.base, Placement([duct[0], DECK - 4.4, duct[2]], a))
    # The pylon: from the deck's edge out to the duct, carrying the turret at its root.
    root = boss_point(s * (ENGINE_GUN_AT[0] - 2), ENGINE_AT[1], 0)
    span = abs(duct[0] - root[0])
    mid = [(duct[0] + root[0]) / 2, 0, duct[2]]
    p.hull.bevel_slab(
        [
            [mid[0] - span / 2, mid[2] - 5],
            [mid[0] + span / 2, mid[2] - 5],
            [mid[0] + span / 2, mid[2] + 5],
            [mid[0] - span / 2, mid[2] + 5],
        ],
        [DECK - 3.5, DECK - 1.2, DECK - 0.2],
        [0, 0.6],
        GREY,
    )
    gun = boss_point(s * ENGINE_GUN_AT[0], ENGINE_GUN_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 5),
        [DECK - 1.5, DECK - 0.4, DECK],
        [0, 0.5],
        M.panel,
        Placement([gun[0], 0, gun[2]]),
    )
    p.neon.ring(5, 0.3, 8, N, Placement([gun[0], DECK - 0.6, gun[2]]))
    p.neon.box([span - 6, 0.3, 0.5], N, Placement([mid[0], DECK - 0.15, mid[2] + 4.6]))


def _ribbed_underside(p: Any, outline: list[Any], y: float) -> None:
    """Add ridges under a flat piece of `outline` (model XZ), along X, their faces 40° off flat.

    The models drop faces turned down: these show as the piece swings and once it hangs.
    """
    xs = [q[0] for q in outline]
    zs = [q[1] for q in outline]
    z0 = min(zs)
    z1 = max(zs)
    x0 = min(xs)
    x1 = max(xs)
    teeth = max(2, round((z1 - z0) / 3))
    step = (z1 - z0) / teeth
    depth = step / 2 * math.tan(40 * math.pi / 180)
    for k in range(teeth):
        a = z0 + k * step
        m = a + step / 2
        b = a + step
        w = _width_at(outline, m)
        xa = max(x0, w[0])
        xb = min(x1, w[1])
        p.hull.face([[xa, y, a], [xb, y, a], [xb, y - depth, m], [xa, y - depth, m]], M.panel)
        p.hull.face([[xa, y - depth, m], [xb, y - depth, m], [xb, y, b], [xa, y, b]], M.panel)


def _width_at(outline: list[Any], z: float) -> list[float]:
    """Return the outline's model X range `[low, high]` at `z`."""
    low = 1e9
    high = -1e9
    n = len(outline)
    for i in range(n):
        a = outline[i]
        b = outline[(i + 1) % n]
        if (a[1] - z) * (b[1] - z) <= 0 and a[1] != b[1]:
            x = a[0] + (z - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            low = min(low, x)
            high = max(high, x)
    return [low, high]


def belt(side: float) -> Any:
    """Return the drawing of the armour belt on `side` (+1 the config's right), swung out flat.

    Heavy grey plates with lit seams, a lit edge, ribbed beneath; its battery's bed on its top
    (FB-CLOUD-DREADNOUGHT-05, FB-CLOUD-DREADNOUGHT-10).
    """

    def draw(p: Any) -> None:
        outline = [pt(side * q[0], q[1]) for q in BELT]
        p.hull.bevel_slab(
            outline, [DECK - BELT_THICK, DECK - 0.8, DECK], [0, 0.6], GREY, None, M.panel
        )
        _ribbed_underside(p, outline, DECK - BELT_THICK)
        # Plate seams across it, lit; a lit strip along its outer edge.
        for y in [-14, -4, 8]:
            w = _width_at(outline, -y)
            p.neon.box(
                [abs(w[1] - w[0]) - 3, 0.25, 0.4], N, Placement([(w[0] + w[1]) / 2, DECK, -y])
            )
        tip = boss_point(side * (BELT[3][0] - 0.6), (BELT[2][1] + BELT[3][1]) / 2, DECK)
        p.neon.box([0.5, 0.3, BELT[3][1] - BELT[2][1]], N, Placement(tip))
        # The battery's bed, dark, lit studs at its corners.
        bed = boss_point(side * BATTERY_AT[0], BATTERY_AT[1], DECK)
        p.bare.box([18, 0.4, 10], M.dark, Placement(bed))
        for dx in [-8, 8]:
            for dz in [-4, 4]:
                p.neon.box([0.8, 0.5, 0.8], N, Placement([bed[0] + dx, DECK, bed[2] + dz]))
        # Its hinge's knuckles along the root.
        for y in [-18, -6, 6, 16]:
            q = boss_point(side * (BELT[0][0] + 0.8), y, DECK - 1.6)
            p.hull.cylinder(1.3, 5, 8, M.base, Placement([q[0], q[1], q[2] - 2.5], 0, math.pi / 2))

    return draw


def plating(p: Any) -> None:
    """Draw the after deck's plating (FB-CLOUD-DREADNOUGHT-11): heavy plates, lit seams, vents."""
    x0, x1, y0, y1 = PLATING[0], PLATING[1], PLATING[2], PLATING[3]
    rows = 3
    for k in range(rows):
        a = y0 + (y1 - y0) * k / rows + 0.3
        b = y0 + (y1 - y0) * (k + 1) / rows - 0.3
        outline = [pt(x0, a), pt(x1, a), pt(x1, b), pt(x0, b)]
        p.hull.bevel_slab(
            outline,
            [DECK, PLATING_TOP - 0.8, PLATING_TOP],
            [0, 0.7],
            GREY if k % 2 == 0 else M.panel,
        )
        if k > 0:
            q = boss_point(0, a - 0.3, PLATING_TOP - 0.6)
            p.neon.box([x1 - x0 - 2, 0.5, 0.4], N, Placement(q))
    for k in range(4):
        q = boss_point(-7.5 + k * 5, y1 - 3, PLATING_TOP)
        p.bare.box([3, 0.3, 2], M.dark, Placement(q))


def hatch(p: Any) -> None:
    """Draw the hatch over the stern rotor (BOSS-58): an armoured cupola, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.lathe(
        [[5.8, DECK], [5.4, DECK + 1.6], [3.4, DECK + 2.8], [0, DECK + 3.2]],
        8,
        GREY,
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    p.neon.ring(5.7, 0.3, 8, N, Placement([at[0], DECK + 0.6, at[2]], math.pi / 8))


def hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the well the rotor rises from."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(5.6, 1, 12, M.base, Placement([at[0], DECK - 0.3, at[2]]))
    p.neon.ring(5.6, 0.3, 12, N, Placement([at[0], DECK + 0.5, at[2]]))


def dreadnought_armour() -> Any:
    """Return the Cloud Dreadnought's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "belt-right": {"whole": belt(1)},
        "belt-left": {"whole": belt(-1)},
        "plating": {"whole": plating},
        "rotor-hatch": {"whole": hatch, "frame": hatch_frame},
    }
