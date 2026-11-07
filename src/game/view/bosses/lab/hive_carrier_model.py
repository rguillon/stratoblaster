# Copyright (c) 2026 Renaud Guillon
"""FB-HIVE-CARRIER-01 to FB-HIVE-CARRIER-05, Lab L-2: the Hive Carrier.

Logical pixels, nose +Z, Y up (towards the camera). A fat hexagonal hive-ship: a waxy shell held by
dark metal ribs, a honeycomb of wax cells over its deck, a domed queen chamber in its middle (the
core), a cell-bay at each slanted corner and a bony ram with its queen gland at its front. Its
combs over the side corners, the chamber's front and its rear are its armour, drawn apart
(`hive_carrier_comb`). Lab boss: in the dev viewer only.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.hive_carrier import DECK_TOP, HIVE_CARRIER
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import strip
from game.view.bosses.lab.hive_carrier_comb import (
    CHAMBER_R,
    HEX,
    draw_core_cells,
    hive_armour,
    model,
    rib_ends,
)
from game.view.bosses.mini_boss_greebles import lamps
from game.view.bosses.mini_boss_shapes import offset
from game.view.bosses.world_1_organic_kit import F, M, barbs, gland, tentacle, vein_line
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["hive-carrier"]
# A sixth of a turn: a hexagonal lathe turned by it puts a flat side to the front.
SIXTH = math.pi / 6
# The queen chamber's profile (radius, height), from the deck to its top.
CHAMBER = [
    [CHAMBER_R, DECK_TOP],
    [CHAMBER_R - 0.5, 9],
    [16, 13.5],
    [10, 17],
    [5, 18.4],
    [0, 18.8],
]


def _flat(points: list[Any]) -> list[Any]:
    """Return design points (px, X right, Y up) as a model outline (x, z)."""
    return [[-q[0], -q[1]] for q in points]


def _draw_shell(p: Any) -> None:
    """Draw the waxy shell (FB-HIVE-CARRIER-02): the hexagonal hull, its deck dark between cells.

    Dark metal bands round its rim with clamps on its side corners, and radial ribs from the queen
    chamber out to its corners, a vein along each.
    """
    p.flesh.bevel_slab(_flat(HEX), [-6, 0, DECK_TOP], [3, 1.4], F.sinew, None, F.graphite)
    rim = [[q[0] * 0.94, q[1] * 0.94] for q in HEX]
    for k in range(6):
        a = rim[k]
        b = rim[(k + 1) % 6]
        strip(p.hull, _flat([a])[0], _flat([b])[0], 2.6, [DECK_TOP - 0.4, DECK_TOP + 1.4], M.base)
    for s in [-1, 1]:
        corner = model(s * 66, 0, -4)
        p.hull.box([5, 11, 7], M.dark, Placement(corner), M.panel)
        lamps(p.neon, [model(s * 62, 0, DECK_TOP + 1.6)], 1.2, N)
    for rib in rib_ends():
        a = _flat([rib[0]])[0]
        b = _flat([rib[1]])[0]
        strip(p.hull, a, b, 3, [DECK_TOP - 0.4, DECK_TOP + 1.8], M.panel)
        start = model(rib[0][0], rib[0][1], DECK_TOP + 1.9)
        end = model(rib[1][0], rib[1][1], DECK_TOP + 1.9)
        vein_line(p, start, end, [0, 0.4, 0], 0.8, N)


def _draw_chamber(p: Any) -> None:
    """Draw the queen chamber (FB-HIVE-CARRIER-02): the core, a waxy hexagonal dome.

    A dark metal collar round its foot, veins down its six edges, the crown turret's pedestal on
    its front (its mount, BOSS-58), a gland and lit larvae on its flanks.
    """
    p.flesh.lathe(CHAMBER, 6, F.slate, Placement([0, 0, 0], SIXTH))
    p.hull.ring(CHAMBER_R + 0.4, 2.2, 6, M.dark, Placement([0, DECK_TOP - 0.2, 0], SIXTH))
    p.vein.ring(CHAMBER_R * 0.97, 0.5, 6, N, Placement([0, DECK_TOP + 2.4, 0], SIXTH))
    for k in range(6):
        a = k * math.pi / 3
        dx = math.cos(a)
        dz = math.sin(a)
        vein_line(
            p,
            [dx * 6, 18.2, dz * 6],
            [dx * 18.6, 9.4, dz * 18.6],
            [dx * 1.2, 1.2, dz * 1.2],
            0.8,
            N,
        )
    # The crown turret's pedestal, on the chamber's front slope.
    p.hull.cylinder(5.6, 4, 6, M.base, Placement(model(0, -13, 13), SIXTH), 5)
    for s in [-1, 1]:
        gland(p, [s * 11, 14.2, -9], 1.4, N)


def _draw_stern(p: Any) -> None:
    """Draw the stern: two reactors in sacs on the rear edge, bone barbs between them."""
    for s in [-1, 1]:
        reactor_sac(p, model(s * 16, 55, 1.5), 3, N)
    barbs(p, model(0, 54, 1), {"count": 3, "spacing": 5, "size": 3, "dir": [0, 0.2, -1]})


def _bay(p: Any, at: Vec3) -> None:
    """Add a cell-bay (FB-HIVE-CARRIER-03) at a corner: a ring of big wax cells in a metal collar.

    A front bay has a lit hive mouth in its middle (its Hornets come out of it); a rear bay a
    pedestal there under its spore cannon (its mount, BOSS-58).
    """
    p.hull.cylinder(13.5, 5, 6, M.base, Placement(offset(at, 0, 5, 0), SIXTH), 12.4)
    p.neon.ring(12.6, 0.5, 6, N, Placement(offset(at, 0, 9.6, 0), SIXTH))
    for k in range(6):
        a = k * math.pi / 3 + SIXTH
        spot = offset(at, math.cos(a) * 7.6, 10, math.sin(a) * 7.6)
        p.flesh.cylinder(4.2, 3.6 + (k % 2) * 0.8, 6, F.bone, Placement(spot), 3.7)
    if at[2] > 0:
        p.hull.cylinder(4.4, 4.6, 6, M.dark, Placement(offset(at, 0, 10, 0)), 4)
        p.vein.cylinder(3, 0.4, 6, N, Placement(offset(at, 0, 14.6, 0)))
        return
    p.hull.cylinder(4.6, 5, 6, M.panel, Placement(offset(at, 0, 10, 0)), 4.2)


def _ram(p: Any, at: Vec3) -> None:
    """Add the ram (FB-HIVE-CARRIER-03): a bony wedge at the front, the queen gland on it.

    Bone mandibles either side of it, a vein ring round the gland and a plate grafted on its crown
    under its five-barrelled turret (its mount, BOSS-58).
    """
    wedge: list[Any] = [[-15, -9], [15, -9], [11, 3], [5, 9.5], [0, 11], [-5, 9.5], [-11, 3]]
    outline = [[at[0] + q[0], at[2] + q[1]] for q in wedge]
    p.flesh.bevel_slab(outline, [-4, 2, 7], [1, 1.6], F.bone, None, F.sinew)
    organ(p.flesh, 7, 8, F.slate, Placement(offset(at, 0, 6, 0), math.pi / 8), 0.36)
    p.vein.ring(6.6, 0.5, 8, N, Placement(offset(at, 0, 7.4, 0), math.pi / 8))
    p.hull.cylinder(5.2, 0.8, 6, M.base, Placement(offset(at, 0, 10.2, 0), SIXTH))
    for s in [-1, 1]:
        tentacle(
            p,
            offset(at, s * 12, 2, -3),
            offset(at, s * 6, 1, 13),
            [s * 4, 0, 0],
            [2.4, 0.3],
            F.bone,
            4,
        )


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the hive rotor (BOSS-58): a hexagonal wax cap on the chamber's top.

    A metal rim and a seam of light round it; it bursts off as the rotor comes into use.
    """
    at = model(0, 6, 17.8)
    p.hull.cylinder(6.6, 1.8, 6, M.panel, Placement(at), 6)
    p.flesh.cylinder(4.4, 1.2, 6, F.bone, Placement(offset(at, 0, 1.8, 0)), 3.6)
    p.neon.ring(6.4, 0.3, 6, N, Placement(offset(at, 0, 1.2, 0)))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = model(0, 6, 17.6)
    p.hull.ring(6.2, 1.6, 12, M.base, Placement(at))
    p.neon.ring(6.2, 0.3, 12, N, Placement(offset(at, 0, 1.4, 0)))


def _armour() -> Any:
    """Return its armour drawings: the combs (`hive_carrier_comb`) and the rotor's hatch."""
    armour: dict[str, Any] = hive_armour()
    armour["rotor-hatch"] = {"whole": _draw_hatch, "frame": _draw_hatch_frame}
    return armour


def build_hive_carrier(scene: Any) -> Any:
    """FB-HIVE-CARRIER-01, FB-HIVE-CARRIER-04: the Hive Carrier.

    A fat hexagonal hive-ship 4 L across with amber veins: a honeycomb over its waxy shell and its
    metal ribs, the queen chamber in its middle (the core: its crown turret and its rotor), a
    cell-bay at each slanted corner and the ram at its front (its parts).
    """

    def core(p: Any) -> None:
        _draw_shell(p)
        draw_core_cells(p)
        _draw_chamber(p)
        _draw_stern(p)

    return build_boss_model(
        HIVE_CARRIER,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "bay-front-left": _bay,
                "bay-front-right": _bay,
                "bay-rear-left": _bay,
                "bay-rear-right": _bay,
                "ram": _ram,
            },
            "armour": _armour(),
        },
    )
