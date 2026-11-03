# Copyright (c) 2026 Renaud Guillon
"""FB-GEYSER-RIG-01 to FB-GEYSER-RIG-07, 4-2: the Geyser Rig.

Logical pixels, nose +Z, Y up (towards the camera). A flying drilling platform: a heavy deck, a
lattice derrick in its middle (the core), two drill arms reaching forward from its bow corners, two
steam vents at its stern, a drone hangar jutting from its bow and a squat cooling tower aft on its
back plating.
FB-GEYSER-RIG-02: a living rock-tick, its back a scorched flesh shell veined molten, a bone spire
over its core, its drills, pipes and guns metal grafts.
"""

import math

from game.config.bosses.world_4.geyser_rig import GEYSER_RIG, RIG_CORE_GUNS
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import mirrored, strip
from game.view.bosses.mini_boss_greebles import lamps, vent
from game.view.bosses.mini_boss_mechanism import conduit
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H
from game.view.bosses.world_3.toucan_jungle import segment
from game.view.bosses.world_4.ash_plains_soot import EMBER, SCORCH, molten_seam
from game.view.bosses.world_4.geyser_rig_armour import GEYSER_RIG_ARMOUR, deck_plates
from game.view.bosses.world_4.geyser_rig_parts import (
    DECK_Y,
    RIG_YELLOW,
    arm_limbs,
    drill_head,
    hangar,
    steam_vent,
)
from game.view.bosses.world_4.living_forge import (
    SKIN,
    back_ribs,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import RibSpec
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The deck seen from above (right half, bow to stern), its stern corners cut.
DECK = mirrored([
    [0, 38],
    [30, 38],
    [44, 26],
    [44, -54],
    [34, -70],
    [0, -70],
])

# The derrick's corner posts: their foot on the deck and their top, half spread (x = z).
DERRICK_FOOT = 9
DERRICK_TOP = 3
DERRICK_HEIGHT = 42
# The deck plate left on the core's deck (the others lie on the armour, `geyser_rig_armour`).
PLATES = [[-26.0, -14.0, 10.0, 14.0]]


def _deck_veins(p: Any, s: float) -> None:
    """FB-GEYSER-RIG-02: its living flesh on the core's deck: a vein between the plating, a gland.

    The veins' stern runs, the ribs over the back and the other glands lie on the back plating.
    """
    magma_vein(
        p,
        [
            [s * 8, DECK_Y + 0.2, 22],
            [s * 13, DECK_Y + 0.2, 4],
            [s * 17, DECK_Y + 0.2, -25],
        ],
        1.3,
    )
    glands(p, [[s * 6, DECK_Y, 30]], 2, RIG_YELLOW)


def _draw_deck(p: Any) -> None:
    """Draw the deck: a dark bevelled slab, yellow neon along its sides.

    Its dressing between the plating: a bone rib over the bow, molten seams, vents, a conduit, a
    deck plate; the pipe racks, hazard paint, ash and soot lie on the armour (`geyser_rig_armour`).
    """
    hull = p.hull
    neon = p.neon
    p.flesh.bevel_slab(DECK, [0, 3, DECK_Y], [2, 1.5], SKIN.base, None, SKIN.dark)
    back_ribs(p, [28], RibSpec(30, DECK_Y - 2, 3.5, 1))
    for s in SIDES:
        _deck_veins(p, s)
        strip(neon, [s * 41.6, 22], [s * 41.6, -52], 0.8, [DECK_Y, DECK_Y + 0.4], RIG_YELLOW)
        molten_seam(p, [s * 12, -6], [s * 24, -20], DECK_Y)
        vent(hull, [s * 22, DECK_Y, -10], [6, 9], 3)
        conduit(hull, [s * 27, DECK_Y + 2, -30], [s * 8, DECK_Y + 2, -12], 1.3, 3)
    reactor_sacs(
        p,
        [
            [18, 3.6, -68],
            [-18, 3.6, -68],
        ],
        3.2,
        EMBER,
    )
    reactor_sacs(p, [[0, 3.6, -70]], 3.6, EMBER)
    deck_plates(hull, PLATES, DECK_Y)


def _derrick_point(x: float, z: float, k: float) -> Vec3:
    """Return a corner post's point at height fraction `k`, its spread narrowing to the top."""
    spread = DERRICK_FOOT + (DERRICK_TOP - DERRICK_FOOT) * k
    return [x * spread, DECK_Y + 3 + DERRICK_HEIGHT * k, z * spread]


def _draw_derrick(p: Any) -> None:
    """Draw the derrick (the core): a lattice tower of four posts braced crosswise.

    Its crown block is lit yellow, the drill pipe glowing hot down its middle.
    """
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    hull.box([26, 3, 26], H.panel, Placement([0, DECK_Y, 0]), SCORCH)
    # FB-GEYSER-RIG-02: a spire of bone, braced by sinews.
    corners = [
        [1, 1],
        [1, -1],
        [-1, -1],
        [-1, 1],
    ]
    for i in range(len(corners)):
        x = corners[i][0]
        z = corners[i][1]
        nxz = corners[(i + 1) % 4]
        nx = nxz[0]
        nz = nxz[1]
        segment(flesh, [_derrick_point(x, z, 0), _derrick_point(x, z, 1)], [1.4, 0.8], SKIN.bone, 4)
        segment(
            flesh,
            [_derrick_point(x, z, 0.08), _derrick_point(nx, nz, 0.45)],
            [0.5, 0.5],
            SKIN.panel,
            4,
        )
        segment(
            flesh,
            [_derrick_point(nx, nz, 0.08), _derrick_point(x, z, 0.45)],
            [0.5, 0.5],
            SKIN.panel,
            4,
        )
        segment(
            flesh,
            [_derrick_point(x, z, 0.45), _derrick_point(nx, nz, 0.8)],
            [0.4, 0.4],
            SKIN.panel,
            4,
        )
    hull.box([9, 4, 9], H.panel, Placement([0, DECK_Y + 3 + DERRICK_HEIGHT, 0]), H.base)
    neon.ring(5, 0.8, 8, RIG_YELLOW, Placement([0, DECK_Y + 4 + DERRICK_HEIGHT, 0], math.pi / 8))
    lamps(neon, [[0, DECK_Y + 7.4 + DERRICK_HEIGHT, 0]], 1.6, EMBER)
    neon.cylinder(1.1, DERRICK_HEIGHT, 6, EMBER, Placement([0, DECK_Y + 3, 0]))


def _draw_gun_house(p: Any) -> None:
    """Draw the drill floor's house at the derrick's foot, its twin fan guns pointing forward."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    hull.box([28, 8, 13], H.base, Placement([0, DECK_Y, 14]), H.panel)
    strip(neon, [-12, 20.6], [12, 20.6], 0.7, [DECK_Y + 6.4, DECK_Y + 7.2], RIG_YELLOW)
    for m in RIG_CORE_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(2.6, 2, 6, H.dark, Placement([x, y, z - 5], 0, QUARTER))
        hull.cylinder(1.4, 3.4, 6, H.dark, Placement([x, y, z - 4], 0, QUARTER))
        charge.cylinder(1.45, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)


def build_geyser_rig(scene: Any) -> Any:
    """Build the Geyser Rig (FB-GEYSER-RIG-01, FB-GEYSER-RIG-06).

    A flying drilling rig with two drill heads and steam vents, yellow neon, soot, ash and molten
    seams on its deck; its back plating with the cooling tower and its wing plates with the pipe
    racks are armour of its own (D-254, `geyser_rig_armour`).
    """

    def core(p: Any) -> None:
        _draw_deck(p)
        _draw_derrick(p)
        _draw_gun_house(p)

    return build_boss_model(
        GEYSER_RIG,
        scene,
        RIG_YELLOW,
        {
            "core": core,
            "parts": {
                "drill-left": drill_head,
                "drill-right": drill_head,
                "vent-left": steam_vent,
                "vent-right": steam_vent,
                "hangar": hangar,
            },
            "limbs": arm_limbs(),
            "armour": GEYSER_RIG_ARMOUR,
        },
    )
