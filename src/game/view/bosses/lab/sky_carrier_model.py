# Copyright (c) 2026 Renaud Guillon
"""FB-SKY-CARRIER-01 to FB-SKY-CARRIER-04: the Sky Carrier, the Lab's L-11 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A flying aircraft carrier: a long hull under a
flat flight deck that overhangs it, its bow tapering to a point; two catapult tracks down the bow,
landing stripes and edge lights on its after deck, the island tower on a sponson on its right edge,
ducted lift engines on sponsons along its hull. The middle of its deck (two halves that slide
apart), its island and its armour are drawn in `sky_carrier_parts`; its boom and lift rotors are its
rig (`sky_carrier_rig`). A machine, not a creature: the Lab's third round builds flying fortresses
(user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.sky_carrier import (
    BOOM_HINGE,
    CATAPULT_X,
    CATAPULT_Y,
    DECK,
    DECK_LOW,
    DECK_TOP,
    FAN_H,
    FAN_RADIUS,
    GUN_H,
    HANGAR_FLOOR,
    HULL_ENDS,
    HULL_HALF,
    HULL_LOW,
    ISLAND,
    LIFT_FANS,
    ROTOR_AT,
    SKY_CARRIER,
    SPLIT,
    STERN_GUN_AT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.sky_carrier_parts import (
    PAINT,
    beam_cannon,
    carrier_armour,
    catapult,
    deck_gun,
    flat,
    island_cupola,
    rect,
)
from game.view.bosses.lab.sky_carrier_rig import build_carrier_rig, carrier_triangles
from game.view.bosses.world_1_organic_kit import F, M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["sky-carrier"]
QUARTER = math.pi / 2
EDGE = DECK[3][0]


def _mirrored(right: list[list[float]]) -> list[list[Any]]:
    """Return a whole outline (model XZ) from its right half (playfield, from the centre line)."""
    points = [flat(q[0], q[1]) for q in right]
    points.extend([flat(-q[0], q[1]) for q in reversed(right) if q[0] != 0])
    return points


def _cut(right: list[list[float]], y0: float, y1: float) -> list[list[float]]:
    """Return the part of a right half outline between `y0` and `y1` (its edges straight across).

    The outline runs from the centre line at one end to the centre line at the other, its X growing
    then shrinking; the cut keeps its points between, adding its edge's X at each cut.
    """
    result: list[list[float]] = [[0, y0]]
    if _x_at(right, y0) > 0:
        result.append([_x_at(right, y0), y0])
    result.extend([q for q in right if y0 < q[1] < y1 and q[0] != 0])
    if _x_at(right, y1) > 0:
        result.append([_x_at(right, y1), y1])
    result.append([0, y1])
    return result


def _x_at(right: list[list[float]], y: float) -> float:
    for k in range(len(right) - 1):
        a = right[k]
        b = right[k + 1]
        if min(a[1], b[1]) <= y <= max(a[1], b[1]) and a[1] != b[1]:
            return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])
    return 0


HULL: list[list[float]] = [
    [0, HULL_ENDS[0] - 2],
    [10, HULL_ENDS[0] + 2],
    [17, HULL_ENDS[0] + 14],
    [HULL_HALF, HULL_ENDS[0] + 28],
    [HULL_HALF, HULL_ENDS[1] - 6],
    [15, HULL_ENDS[1]],
    [0, HULL_ENDS[1]],
]


def _hull(p: Any) -> None:
    """Draw the hull (FB-SKY-CARRIER-02): a long armoured keel under the deck, open amidships.

    Its lower hull runs its whole length up to the hangar's floor; over it, its upper hull fore and
    aft of the hangar, and the hangar's walls between: a dark floor with lit lane lines, its
    walls lined with bays, where the deck's halves open. Rows of lit ports down its sides.
    """
    p.hull.bevel_slab(
        _mirrored(HULL), [HULL_LOW, HANGAR_FLOOR - 0.6, HANGAR_FLOOR], [3, 0], M.base, None, M.dark
    )
    for y0, y1 in [[HULL_ENDS[0] - 2, SPLIT[0]], [SPLIT[1], HULL_ENDS[1]]]:
        p.hull.slab(
            _mirrored(_cut(HULL, y0, y1)), [HANGAR_FLOOR - 0.2, DECK_LOW], M.panel, None, M.base
        )
    for side in [-1, 1]:
        wall = rect(side * (HULL_HALF - 3), side * HULL_HALF, SPLIT[0], SPLIT[1])
        p.hull.slab(wall, [HANGAR_FLOOR - 0.2, DECK_LOW], M.panel, None, M.base)
        for k in range(4):
            y = SPLIT[0] + 6 + k * 11
            p.bare.box(
                [0.4, 4, 7],
                M.dark,
                Placement(boss_point(side * (HULL_HALF - 3.1), y, HANGAR_FLOOR + 1)),
            )
            p.neon.box(
                [0.4, 0.5, 7],
                N,
                Placement(boss_point(side * (HULL_HALF - 3.15), y, HANGAR_FLOOR + 5.2)),
            )
        for y in [-80, -66, 0, 14, 28, 42, 56]:
            p.neon.box(
                [0.4, 1, 3],
                N,
                Placement(boss_point(side * (_x_at(HULL, y) + 0.05), y, HANGAR_FLOOR + 2)),
            )
    for x in [-8, 8]:
        p.neon.box(
            [0.6, 0.3, SPLIT[1] - SPLIT[0] - 2],
            N,
            Placement(boss_point(x, (SPLIT[0] + SPLIT[1]) / 2, HANGAR_FLOOR)),
        )
    for k in range(4):
        y = SPLIT[0] + 4 + k * 12
        p.bare.box([28, 0.4, 1.6], PAINT, Placement(boss_point(0, y, HANGAR_FLOOR)))


def _edge_lights(p: Any) -> None:
    """Draw lights down both edges of the deck, fore and aft of its split (not by the island)."""
    for side in [-1, 1]:
        for k in range(9):
            y = -76 + k * 16
            if SPLIT[0] <= y <= SPLIT[1] or (side > 0 and ISLAND[2] - 2 < y < ISLAND[3] + 2):
                continue
            at = boss_point(side * (EDGE - 0.8), y, DECK_TOP - 0.1)
            p.neon.box([0.8, 0.5, 0.8], N, Placement(at))


def _deck(p: Any) -> None:
    """Draw the flight deck fore and aft of its split middle (FB-SKY-CARRIER-02).

    Plated slabs overhanging the hull; on the bow, the two catapult tracks lit along their sides
    and the boom's hinge block; on the after deck, the landing centre line, stripes across its
    stern, an elevator; edge lights all round; the island's sponson on the right edge.
    """
    for y0, y1 in [[DECK[0][1], SPLIT[0]], [SPLIT[1], DECK[len(DECK) - 1][1]]]:
        p.flesh.bevel_slab(
            _mirrored(_cut(DECK, y0, y1)),
            [DECK_LOW, DECK_TOP - 0.8, DECK_TOP],
            [0, 0.5],
            F.graphite,
            None,
            F.slate,
        )
    for side in [-1, 1]:
        x = side * CATAPULT_X
        length = CATAPULT_Y[1] - CATAPULT_Y[0]
        mid = (CATAPULT_Y[0] + CATAPULT_Y[1]) / 2
        p.bare.box([1.4, 0.3, length], M.dark, Placement(boss_point(x, mid, DECK_TOP)))
        for dx in [-1.3, 1.3]:
            p.neon.box([0.35, 0.35, length - 2], N, Placement(boss_point(x + dx, mid, DECK_TOP)))
    # The boom's hinge block at the bow's tip.
    hinge = boss_point(0, BOOM_HINGE[0] + 2, DECK_TOP)
    p.hull.box([9, 1.2, 4], M.panel, Placement(hinge))
    # The after deck: its landing centre line, stripes across its stern, an elevator.
    for k in range(5):
        y = SPLIT[1] + 4 + k * 9
        if abs(y - STERN_GUN_AT[1]) > 8:
            p.bare.box([1.2, 0.3, 5], PAINT, Placement(boss_point(0, y + 2.5, DECK_TOP)))
    for x in [-18, -12, 12, 18]:
        p.bare.box([2, 0.3, 8], PAINT, Placement(boss_point(x, 62, DECK_TOP)))
    for v in [-1, 1]:
        p.bare.box([12, 0.3, 0.8], PAINT, Placement(boss_point(-13, 16 + v * 6, DECK_TOP)))
        p.bare.box([0.8, 0.3, 12], PAINT, Placement(boss_point(-13 + v * 6, 16, DECK_TOP)))
    # The island's sponson: the deck carried out under it, on a bracket.
    sponson = rect(EDGE - 1, ISLAND[1] + 1, ISLAND[2] - 2, ISLAND[3] + 2)
    p.flesh.bevel_slab(
        sponson, [DECK_LOW, DECK_TOP - 0.8, DECK_TOP], [1.4, 0.5], F.graphite, None, F.slate
    )
    # The core's gun seats: the stern turret's barbette, the rotor's well.
    gun = boss_point(STERN_GUN_AT[0], STERN_GUN_AT[1], 0)
    p.hull.cylinder(
        6.6, GUN_H - DECK_TOP + 0.2, 10, M.panel, Placement([gun[0], DECK_TOP - 0.2, gun[2]])
    )
    p.neon.ring(6.7, 0.4, 10, N, Placement([gun[0], DECK_TOP + 0.3, gun[2]]))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.cylinder(6.2, 0.6, 8, M.dark, Placement([well[0], DECK_TOP - 0.5, well[2]]))


def _lift_fans(p: Any) -> None:
    """Draw the lift engines (FB-SKY-CARRIER-02): a duct on a sponson out from the hull's side.

    A thick ring with a lit lip, cross struts and a hub bearing under the rotor (the rotor is the
    rig's), its sponson arm back to the hull.
    """
    for q in LIFT_FANS:
        side = 1 if q[0] > 0 else -1
        at = boss_point(q[0], q[1], 0)
        p.hull.lathe(
            [
                [FAN_RADIUS + 1.4, FAN_H - 1.5],
                [FAN_RADIUS + 1.6, FAN_H + 1],
                [FAN_RADIUS + 0.4, FAN_H + 2.2],
            ],
            12,
            M.panel,
            Placement(at),
            False,
        )
        p.bare.ring(FAN_RADIUS + 0.2, 3.7, 12, M.base, Placement([at[0], FAN_H - 1.5, at[2]]))
        p.bare.cylinder(FAN_RADIUS + 0.3, 0.4, 12, M.dark, Placement([at[0], FAN_H - 1.6, at[2]]))
        p.neon.ring(FAN_RADIUS + 0.7, 0.4, 12, N, Placement([at[0], FAN_H + 2, at[2]]))
        p.bare.box([FAN_RADIUS * 2, 0.6, 1], M.dark, Placement([at[0], FAN_H - 0.4, at[2]]))
        p.bare.cylinder(1.4, 1.6, 6, M.base, Placement([at[0], FAN_H - 0.6, at[2]]))
        inner = side * (HULL_HALF - 1)
        outer = side * (abs(q[0]) - FAN_RADIUS - 1)
        arm = [
            flat(inner, q[1] - 4),
            flat(outer, q[1] - 3),
            flat(outer, q[1] + 3),
            flat(inner, q[1] + 4),
        ]
        p.hull.bevel_slab(
            arm, [FAN_H - 2, FAN_H + 0.5, FAN_H + 1.2], [0, 0.4], M.base, None, M.panel
        )


def build_sky_carrier(scene: Any) -> Any:
    """FB-SKY-CARRIER-01, FB-SKY-CARRIER-04: the Sky Carrier.

    A flying aircraft carrier: a flat flight deck over a long hull, catapults down its bow, an
    island tower on its right edge, ducted lift engines along its sides; orange light lines
    (shown yellow); about 5 L long.
    """

    def core(p: Any) -> None:
        _hull(p)
        _deck(p)
        _edge_lights(p)
        _lift_fans(p)

    return build_boss_model(
        SKY_CARRIER,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "deck-left": deck_gun,
                "deck-right": deck_gun,
                "catapult-left": catapult,
                "catapult-right": catapult,
                "island": island_cupola,
                "beam": beam_cannon,
            },
            # FB-SKY-CARRIER-11: the beam's boom swings over the bow; its lift rotors spin.
            "rig": {"build": build_carrier_rig, "triangles": carrier_triangles},
            "armour": carrier_armour(),
        },
    )
