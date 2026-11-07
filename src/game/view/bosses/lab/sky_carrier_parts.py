# Copyright (c) 2026 Renaud Guillon
"""FB-SKY-CARRIER-03, FB-SKY-CARRIER-05: the Sky Carrier's moving pieces, shed armour and parts.

Logical pixels, nose +Z, Y up (towards the camera). The two halves of the middle of its flight
deck (moving pieces that slide apart, BOSS-45), its island tower (a moving piece that folds down
outboard), the plating of its bow quarters and the hatch over its stern rotor (shed), and the
drawings of its parts: the deck guns' barbettes, the catapults' launch cradles, the island's laser
cupola and the beam cannon at the end of its boom.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.sky_carrier import (
    BEAM_H,
    BOW_PLATING,
    DECK,
    DECK_GUN_AT,
    DECK_LOW,
    DECK_TOP,
    GUN_H,
    ISLAND,
    ISLAND_LASER_AT,
    ISLAND_TOP,
    MAST_TOP,
    PLATING_TOP,
    ROTOR_AT,
    SPLIT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.world_1_organic_kit import F, M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["sky-carrier"]
QUARTER = math.pi / 2
# Deck paint: light lines on the dark deck (shown in the body shades).
PAINT = [0.3, 0.3, 0.33]
EDGE = DECK[3][0]


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def rect(x0: float, x1: float, y0: float, y1: float) -> list[list[Any]]:
    """Return the playfield rectangle `[x0, x1] x [y0, y1]` as a model outline."""
    return [flat(x0, y0), flat(x1, y0), flat(x1, y1), flat(x0, y1)]


def deck_half(side: float) -> Any:
    """Return the drawing of the split deck's half on `side` (+1: right), as it rests.

    A plated slab from the centre line out to the deck's edge: a lit seam along its split edge,
    the half centre line's dashes, an elevator's outline, edge lights; the right one carries the
    seat of its deck gun.
    """

    def draw(p: Any) -> None:
        p.flesh.bevel_slab(
            rect(0.2 * side, side * EDGE, SPLIT[0], SPLIT[1]),
            [DECK_LOW, DECK_TOP - 0.8, DECK_TOP],
            [0, 0.5],
            F.graphite,
            None,
            F.slate,
        )
        p.neon.box(
            [0.5, 0.4, SPLIT[1] - SPLIT[0] - 2],
            N,
            Placement(boss_point(side * 0.8, (SPLIT[0] + SPLIT[1]) / 2, DECK_TOP - 0.2)),
        )
        for k in range(3):
            y = SPLIT[0] + 6 + k * 14
            p.bare.box([1.2, 0.3, 6], PAINT, Placement(boss_point(side * 2.2, y + 3, DECK_TOP)))
        # The elevator: a square inset by the deck gun, its edge painted.
        ex = side * 9
        for v in [-1, 1]:
            p.bare.box([12, 0.3, 0.8], PAINT, Placement(boss_point(ex, -12 + v * 6, DECK_TOP)))
            p.bare.box([0.8, 0.3, 12], PAINT, Placement(boss_point(ex + v * 6, -12, DECK_TOP)))
        for k in range(4):
            y = SPLIT[0] + 4 + k * 12
            p.neon.box(
                [0.8, 0.5, 0.8], N, Placement(boss_point(side * (EDGE - 0.8), y, DECK_TOP - 0.1))
            )
        gun = boss_point(side * DECK_GUN_AT[0], DECK_GUN_AT[1], 0)
        p.hull.cylinder(6.2, 0.8, 10, M.panel, Placement([gun[0], DECK_TOP - 0.2, gun[2]]))
        # A walkway hung on its outer edge.
        p.hull.box(
            [1.6, 1.2, SPLIT[1] - SPLIT[0] - 4],
            M.base,
            Placement(boss_point(side * (EDGE + 0.8), (SPLIT[0] + SPLIT[1]) / 2, DECK_TOP - 2.4)),
        )

    return draw


def draw_island(p: Any) -> None:
    """Draw the island tower (FB-SKY-CARRIER-02), as it rests on its sponson on the right edge.

    A tall plated block, a narrower bridge on it with a lit window band all round, a raked stack
    behind it, a lattice mast on its roof with a radar bar and a yard; folds down outboard as one
    piece.
    """
    x0 = ISLAND[0]
    x1 = ISLAND[1]
    y0 = ISLAND[2]
    y1 = ISLAND[3]
    p.hull.bevel_slab(rect(x0, x1, y0, y1), [DECK_TOP, 27, 28], [0, 0.8], M.panel, None, M.base)
    p.hull.bevel_slab(
        rect(x0 + 1.5, x1 - 1.5, y0 + 3, y1 - 8),
        [28, ISLAND_TOP - 1, ISLAND_TOP],
        [0, 0.7],
        M.base,
        None,
        M.panel,
    )
    cx = (x0 + x1) / 2
    for side in [-1, 1]:
        x = cx + side * ((x1 - x0) / 2 - 1.5 + 0.05)
        p.neon.box([0.4, 1.2, y1 - y0 - 12], N, Placement(boss_point(x, (y0 + 3 + y1 - 8) / 2, 32)))
    p.neon.box([x1 - x0 - 3.2, 1.2, 0.4], N, Placement(boss_point(cx, y0 + 2.95, 32)))
    for k in range(3):
        p.bare.box([x1 - x0 - 1, 0.6, 1.2], M.dark, Placement(boss_point(cx, y0 + 5 + k * 6, 27.5)))
    # The stack behind the bridge: a raked block, its smoke vents dark, a lit band.
    p.hull.bevel_slab(
        rect(x0 + 2.5, x1 - 2.5, y1 - 7, y1 - 1.5), [28, 33, 34], [0, 0.8], M.panel, None, M.dark
    )
    p.neon.box([x1 - x0 - 4.8, 0.5, 0.5], N, Placement(boss_point(cx, y1 - 1.6, 31)))
    # The mast: a lattice post, a radar bar across it, a yard with lights.
    mast = boss_point(cx, y0 + 15, ISLAND_TOP)
    p.hull.cylinder(1, MAST_TOP - ISLAND_TOP, 4, M.base, Placement(mast), 0.5)
    p.hull.box([9, 1.2, 1.4], M.panel, Placement([mast[0], MAST_TOP - 4, mast[2]]))
    p.neon.box([9.4, 0.4, 0.4], N, Placement([mast[0], MAST_TOP - 3.3, mast[2] + 0.6]))
    p.hull.box([6, 0.5, 0.5], M.base, Placement([mast[0], MAST_TOP - 1.2, mast[2]]))
    for dx in [-3, 3]:
        p.neon.box([0.8, 0.8, 0.8], N, Placement([mast[0] + dx, MAST_TOP - 0.8, mast[2]]))
    # Hull numbers' ghost: two light plates on its outer face.
    for k in range(2):
        p.bare.box([0.3, 5, 3], PAINT, Placement(boss_point(x1 + 0.05, y0 + 6 + k * 4.5, 19)))


def draw_bow_plating(p: Any) -> None:
    """Draw the bow quarters' armour (FB-SKY-CARRIER-11): heavy plates, lit seams, rivets."""
    for side in [-1, 1]:
        outline = [flat(side * q[0], q[1]) for q in BOW_PLATING]
        p.hull.bevel_slab(
            outline,
            [DECK_TOP - 0.3, PLATING_TOP - 0.9, PLATING_TOP],
            [0, 1.1],
            M.panel,
            None,
            M.base,
        )
        p.neon.box([0.5, 0.4, 14], N, Placement(boss_point(side * 19, -71, PLATING_TOP)))
        for y in [-64, -69, -74, -79]:
            p.bare.box(
                [0.9, 0.4, 0.9], M.dark, Placement(boss_point(side * 14, y, PLATING_TOP - 0.6))
            )


def draw_hatch(p: Any) -> None:
    """Draw the hatch over the stern rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.6),
        [DECK_TOP - 0.3, DECK_TOP + 0.6, DECK_TOP + 1.8],
        [0, 0.9],
        M.panel,
        Placement(at),
    )
    p.neon.ring(6.2, 0.25, 8, N, Placement([at[0], DECK_TOP + 0.9, at[2]], math.pi / 8))


def draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6.4, 1.2, 12, M.base, Placement([at[0], DECK_TOP - 0.4, at[2]]))
    p.neon.ring(6.4, 0.3, 12, N, Placement([at[0], DECK_TOP + 0.6, at[2]]))


def carrier_armour() -> Any:
    """Return the Sky Carrier's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "deck-right": {"whole": deck_half(1)},
        "deck-left": {"whole": deck_half(-1)},
        "island": {"whole": draw_island},
        "bow-plating": {"whole": draw_bow_plating},
        "rotor-hatch": {"whole": draw_hatch, "frame": draw_hatch_frame},
    }


def deck_gun(p: Any, at: Vec3) -> None:
    """Add a deck gun's barbette (FB-SKY-CARRIER-03): an armoured drum, lit, splinter plates."""
    p.hull.bevel_slab(
        polygon(8, 5.4),
        [DECK_TOP, GUN_H - 0.5, GUN_H],
        [0, 0.4],
        M.panel,
        Placement([at[0], 0, at[2]], math.pi / 8),
        M.base,
    )
    p.neon.ring(5.45, 0.4, 8, N, Placement([at[0], DECK_TOP + 0.3, at[2]], math.pi / 8))
    for k in range(3):
        a = math.pi * 0.75 + k * math.pi / 4
        q = [at[0] + math.sin(a) * 6.5, DECK_TOP, at[2] + math.cos(a) * 6.5]
        p.hull.box([3.4, 2, 0.9], M.base, Placement(q, a))


def catapult(p: Any, at: Vec3) -> None:
    """Add a catapult's launch cradle (FB-SKY-CARRIER-03): a shuttle on its track and its aircraft.

    An armoured shuttle block astride the track, a parked dart-winged drone on it lit along its
    spine, and the blast deflector raised behind it.
    """
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        rect(-x - 3.5, -x + 3.5, -z - 6, -z + 4),
        [DECK_TOP, DECK_TOP + 1.6, DECK_TOP + 2.2],
        [0, 0.6],
        M.panel,
        None,
        M.base,
    )
    wing = [
        [x, z + 7],
        [x + 5, z - 2],
        [x + 1.5, z - 1],
        [x, z - 4],
        [x - 1.5, z - 1],
        [x - 5, z - 2],
    ]
    p.hull.slab(wing, [DECK_TOP + 2.2, DECK_TOP + 3.2], M.base, None, M.panel)
    p.neon.box([0.6, 0.4, 7], N, Placement([x, DECK_TOP + 3.2, z + 1.5]))
    p.neon.box([2.4, 0.4, 0.6], N, Placement([x, DECK_TOP + 2.2, z - 5.6]))
    # The blast deflector: a plate raised at an angle behind it.
    p.hull.box([7.5, 0.8, 4], M.panel, Placement([x, DECK_TOP + 0.2, z - 8.5], 0, -0.6))


def island_cupola(p: Any, _at: Vec3) -> None:
    """Add the island's fire-control cupola (FB-SKY-CARRIER-03): its laser turret's seat."""
    gun = boss_point(ISLAND_LASER_AT[0], ISLAND_LASER_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 4.8),
        [ISLAND_TOP - 0.2, ISLAND_TOP + 0.3, ISLAND_TOP + 0.6],
        [0, 0.4],
        M.panel,
        Placement([gun[0], 0, gun[2]], math.pi / 8),
    )
    p.neon.ring(4.85, 0.3, 8, N, Placement([gun[0], ISLAND_TOP, gun[2]], math.pi / 8))


def beam_cannon(p: Any, at: Vec3) -> None:
    """Add the beam cannon's cradle at the boom's end (FB-SKY-CARRIER-11), its emitter on top.

    An armoured block clamped round the boom's end, under its laser mount (BOSS-58), lit along its
    sides, and two heat-sink fins standing either side of the emitter.
    """
    h = BEAM_H
    p.hull.bevel_slab(
        rect(-8.5, 8.5, -at[2] - 7, -at[2] + 5),
        [h - 4.5, h - 0.8, h],
        [0, 0.8],
        M.panel,
        None,
        M.base,
    )
    for side in [-1, 1]:
        p.neon.box([0.4, 1, 9], N, Placement([side * 8.55, h - 3, at[2] + 1]))
        p.hull.box([1.2, 5, 7], M.base, Placement([side * 7.6, h, at[2] + 1]))
        p.neon.box([1.3, 0.4, 5], N, Placement([side * 7.6, h + 5, at[2] + 1]))
