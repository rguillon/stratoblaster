# Copyright (c) 2026 Renaud Guillon
"""FB-GEYSER-RIG-03 to FB-GEYSER-RIG-05, 4-2: the Geyser Rig's parts.

Its two drill heads on their swinging arms (moving limbs, FB-GEYSER-RIG-07, D-061), its two steam
vents and its drone hangar. Logical pixels, nose +Z, Y up.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_4.geyser_rig import (
    DRILL_HEIGHT,
    DRILL_REACH,
    RIG_DRILL,
    RIG_DRILL_GUN,
    RIG_SHOULDER,
    RIG_SIDES,
    RIG_VENT_TOP,
    side_sign,
)
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_greebles import lamps, rect, vent
from game.view.bosses.mini_boss_mechanism import conduit, ram
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset
from game.view.bosses.world_3.toucan_jungle import segment
from game.view.bosses.world_4.ash_plains_soot import EMBER, SOOT, ash_drift
from game.view.bosses.world_4.living_forge import SKIN, glands
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Rgb = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


def _neon_or(kind: str, fallback: Rgb) -> Rgb:
    """`BOSS_LOOK.neon[kind] ?? fallback`."""
    colour: Rgb = BOSS_LOOK.neon[kind]
    if colour == None:
        return fallback
    return colour


def _sign(v: float) -> float:
    """`Math.sign`."""
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


# The Rig's yellow neon (FB-GEYSER-RIG-06).
RIG_YELLOW = _neon_or("geyser-rig", [1, 0.88, 0.1])
# Height of the rig's deck.
DECK_Y = 7


def _arm_points(side: str) -> list[Vec3]:
    """Return the model-space points of the `side` drill arm at rest.

    Its shoulder and its drill head.
    """
    s = side_sign(side)
    return [
        boss_point(s * RIG_SHOULDER[0], RIG_SHOULDER[1], DRILL_HEIGHT.shoulder),
        boss_point(s * RIG_DRILL[0], RIG_DRILL[1], DRILL_HEIGHT.head),
    ]


def _drill_arm(side: str) -> Any:
    """Return the `side` drill arm, on its shoulder joint.

    A heavy boom, a ram along it, a yellow line.
    """

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        flesh = p.flesh
        points = _arm_points(side)
        shoulder = points[0]
        head = points[1]
        back = offset(head, 0, 1, -7)
        hull.cylinder(
            5.4,
            DRILL_HEIGHT.shoulder + 2 - DECK_Y,
            8,
            H.dark,
            Placement(offset(shoulder, 0, DECK_Y - DRILL_HEIGHT.shoulder, 0)),
        )
        hull.cylinder(4.4, 2.6, 8, H.panel, Placement(offset(shoulder, 0, 2, 0)), 3.6)
        # FB-GEYSER-RIG-03: a muscled flesh arm, a sinew along its back.
        segment(flesh, [shoulder, back], [3.6, 3], SKIN.base, 6)
        segment(
            flesh,
            [offset(shoulder, 0, 3, 0), offset(back, 0, 2.6, 0)],
            [1.4, 1.2],
            SKIN.panel,
            4,
        )
        segment(
            neon,
            [offset(shoulder, 0, 4.3, 0), offset(back, 0, 3.8, 0)],
            [0.4, 0.35],
            RIG_YELLOW,
            4,
        )
        ram(
            hull,
            offset(shoulder, -side_sign(side) * 4, -1, 2),
            offset(back, -side_sign(side) * 3, -2, -3),
            1.4,
        )

    return draw


def arm_limbs() -> Any:
    """Return the limbs of the two drill arms (FB-GEYSER-RIG-07).

    Each boom is on its shoulder joint.
    """
    limbs = {}
    for side in RIG_SIDES:
        limbs["arm-" + side] = record({"draw": _drill_arm(side)})
    return limbs


def drill_head(p: Any, at: Vec3) -> None:
    """Add a drill head around its centre `at` (FB-GEYSER-RIG-03).

    A ribbed motor housing, a long fluted bit glowing hot at its root, and the gun on top of the
    housing that fires aimed bursts.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    bit_root = at[2] + 6
    p.flesh.cylinder(7.4, 14, 8, SKIN.base, Placement(offset(at, 0, 0, -8), 0, QUARTER))
    for dz in [-6, 0]:
        hull.cylinder(8, 1.6, 8, H.panel, Placement(offset(at, 0, 0, dz), 0, QUARTER))
    neon.ring(8.1, 0.6, 8, RIG_YELLOW, Placement(offset(at, 0, 0, 3.4), 0, QUARTER))
    neon.ring(5.2, 1, 8, EMBER, Placement([at[0], at[1], bit_root], 0, QUARTER))
    hull.cylinder(
        5.6,
        DRILL_REACH - 6,
        8,
        SHADE["edge"],
        Placement([at[0], at[1], bit_root], 0, QUARTER),
        0,
    )
    for k in [0, 1, 2]:
        roll = (k * 2 * math.pi) / 3
        flute = offset(at, math.cos(roll) * 3.6, math.sin(roll) * 3.6, 9)
        hull.box([1.2, 1.2, 12], SOOT, Placement(flute, -math.cos(roll) * 0.12, 0, roll))
    s = _sign(at[0])
    guns = RIG_DRILL_GUN if s > 0 else mirror(RIG_DRILL_GUN)
    for m in guns:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.box([5, 3.8, 8], H.panel, Placement([x, y - 2.4, z - 10]), H.base)
        hull.cylinder(1.4, 7.4, 6, H.dark, Placement([x, y, z - 8], 0, QUARTER))
        charge.cylinder(1.45, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)


# A vent stack's flared top (a lathe profile, from the deck up, around the stack's centre).
STACK = [
    [6.4, 0.0],
    [6.0, 3.0],
    [4.6, 5.0],
    [4.0, 12.0],
    [5.4, 14.6],
    [5.8, 16.4],
]


def steam_vent(p: Any, at: Vec3) -> None:
    """Add a steam vent around its centre `at` (FB-GEYSER-RIG-04).

    A scorched stack rising from a valve block, its flared mouth ringed with yellow neon, hot metal
    glowing in it, ash settled round its foot.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    s = _sign(at[0])
    source = RIG_VENT_TOP if s > 0 else mirror(RIG_VENT_TOP)
    if len(source) > 0:
        m = source[0]
        top = boss_point(m[0], m[1], m[2])
    else:
        top = offset(at, 0, 24, 0)
    hull.box([15, 3, 15], H.base, Placement(offset(at, 0, DECK_Y - 1, 0)), H.panel)
    # FB-GEYSER-RIG-04: a steaming flesh blowhole on a metal valve block.
    p.flesh.lathe(
        STACK,
        8,
        SKIN.panel,
        Placement(offset(at, 0, DECK_Y + 1.4, 0), math.pi / 8),
        False,
    )
    neon.ring(5.9, 0.6, 8, RIG_YELLOW, Placement(offset(top, 0, -2.6, 0), math.pi / 8))
    hull.cylinder(5.2, 0.4, 8, SOOT, Placement(offset(top, 0, -4.2, 0)))
    neon.ring(3.4, 1.2, 8, EMBER, Placement(offset(top, 0, -3.6, 0)))
    charge.cylinder(2.6, 0.6, 8, WHITE, Placement(offset(top, 0, -0.6, 0)))
    muzzle(top, "ring")
    for side in SIDES:
        hull.cylinder(
            1.6,
            3,
            6,
            H.dark,
            Placement(offset(at, side * 6, DECK_Y + 2, 5), 0, 0, QUARTER),
        )
    conduit(hull, offset(at, s * -6, DECK_Y + 2, -2), offset(at, s * -15, DECK_Y + 2, -2), 1.2, 2)
    ash_drift(hull, offset(at, s * 5.5, DECK_Y + 2, -6), 2.6, at[0])


def hangar(p: Any, at: Vec3) -> None:
    """Add the drone hangar around its centre `at` (FB-GEYSER-RIG-05).

    A bay jutting from the bow, its open door framed in yellow, where its Hornets leave from;
    warning lamps either side.
    """
    hull = p.hull
    neon = p.neon
    # FB-GEYSER-RIG-05: a brood sac jutting from the bow, its mouth framed in metal.
    p.flesh.bevel_slab(
        rect(28, 24),
        [DECK_Y - 5, DECK_Y, DECK_Y + 6],
        [1, 1.5],
        SKIN.base,
        Placement(at),
        SKIN.dark,
    )
    glands(
        p,
        [offset(at, -6, DECK_Y + 5.5, 2), offset(at, 6, DECK_Y + 5.5, -2)],
        1.6,
        RIG_YELLOW,
    )
    hull.box([18, 6, 0.8], H.dark, Placement(offset(at, 0, DECK_Y - 2, 11.8)))
    neon.box([20, 0.8, 0.6], RIG_YELLOW, Placement(offset(at, 0, DECK_Y + 4, 12.2)))
    for s in SIDES:
        neon.box([0.8, 6, 0.6], RIG_YELLOW, Placement(offset(at, s * 9.8, DECK_Y - 2, 12.2)))
        lamps(neon, [offset(at, s * 12, DECK_Y + 6, 9)], 1.2, EMBER)
    vent(hull, offset(at, 0, DECK_Y + 6, -3), [14, 9], 4)
    ash_drift(hull, offset(at, 8, DECK_Y + 6, 4), 2.4, 1.7)
    ash_drift(hull, offset(at, -8, DECK_Y + 6, -6), 2, 0.4)
