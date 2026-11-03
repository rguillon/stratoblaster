# Copyright (c) 2026 Renaud Guillon
"""The Narwhal's hull dressing (FB-NARWHAL-02, FB-NARWHAL-05, 2-1).

Phase 7 review: detail and some asymmetry, World 2 frost. Logical pixels, nose +Z, Y up. The
dressing of its back and hump lies on its armour (FB-NARWHAL-06, `narwhal_armour`).
"""

from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.mini_boss_greebles import lamps, mast, plate, rect
from game.view.bosses.world_2.narwhal_hull import half_width
from game.view.bosses.world_2.w2_organic import ICE_FLESH
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from game.view.enemies.enemy_mesh import EnemyParts

type Rgb = list[float]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
# Light metal: worn edges, rails.
EDGE = [0.24, 0.24, 0.27]
# Navigation lights: red to port (+X, the screen's left), green to starboard.
PORT_RED = [1, 0.1, 0.12]
STARBOARD_GREEN = [0.2, 1, 0.35]


# The gap in the gill slits by the hump.
_SLIT_GAP_FROM = -6
_SLIT_GAP_TO = 14


def hull_dressing(p: EnemyParts, n: Rgb) -> None:
    """Add the dressing along both flanks and on the belly (the core's).

    Along both flanks: rows of dark free-flood slots, its bow planes; on its belly a sonar window
    lit teal.
    """
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        # FB-NARWHAL-02: gill slits down the flanks.
        for z in range(-44, 35, 8):
            if z > _SLIT_GAP_FROM and z < _SLIT_GAP_TO:
                continue
            flesh.box(
                [0.6, 1.4, 3.6],
                ICE_FLESH.seam,
                Placement([s * (half_width(z) + 0.1), 1.6, z]),
            )
        bow_plane = [
            [s * 11, 44],
            [s * 19, 40],
            [s * 19, 36],
            [s * 11, 36],
        ]
        flesh.bevel_slab(
            bow_plane,
            [4.5, 5.5, 6.5],
            [0.3, 0.6],
            ICE_FLESH.sinew,
            None,
            ICE_FLESH.rime,
        )
    neon.box([5, 0.5, 6], n, Placement([0, -5.6, 40]))


def back_dressing(p: EnemyParts, n: Rgb) -> None:
    """Add the dressing on its back behind the hump (FB-NARWHAL-05), on the back's armour.

    A blowhole with its grafted metal valve, an escape hatch and a whip antenna off-centre.
    """
    hull = p.hull
    p.flesh.cylinder(2.4, 2.2, 6, ICE_FLESH.sinew, Placement([-3, 15.6, -33]), 1.6)
    hull.cylinder(1.6, 0.6, 8, EDGE, Placement([-3, 17.8, -33]))
    plate(hull, rect(4, 4), [17.4, 0.5], H.panel, Placement([-3, 0, -13]))
    mast(p, [2.5, 15, -40], 4, n)


def hump_dressing(p: EnemyParts, n: Rgb) -> None:
    """Add the dressing on the hump and the forward deck (FB-NARWHAL-05), on the spine's armour.

    A frozen crust on the forward deck, a whip antenna off-centre on the hump, navigation lamps
    on its flanks and its front windows, lit teal.
    """
    neon = p.neon
    crust = [
        [-4, 33],
        [3, 34],
        [5, 41],
        [1, 45],
        [-4, 42],
    ]
    p.flesh.slab(crust, [12.5, 16.4], ICE_FLESH.crystal, None, ICE_FLESH.rime)
    mast(p, [-3, 27, -1], 5, n)
    lamps(neon, [[5.2, 20, 8]], 1.2, PORT_RED)
    lamps(neon, [[-5.2, 20, 8]], 1.2, STARBOARD_GREEN)
    # The hump's front windows, lit teal.
    neon.box([4, 0.9, 0.4], n, Placement([0, 21.6, 22.1]))
