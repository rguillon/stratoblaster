# Copyright (c) 2026 Renaud Guillon
"""The Harbour Kraken (FB-HARBOUR-KRAKEN-01 to FB-HARBOUR-KRAKEN-07, 2-2).

Logical pixels, nose +Z, Y up (towards the camera). A cargo ship flying over the harbour: a long
hull, a forecastle with its laser emitter and twin guns, a bridge tower amidships, four crane
pedestals, the container bay at the stern. Its shell's fore and aft sections and the forecastle are
armour drawn apart (`harbour_kraken_armour`, D-254).
"""

from game.config.bosses.world_2.harbour_kraken import CRANE_REST, HARBOUR_KRAKEN
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import barrels, edge_strips, mirrored
from game.view.bosses.mini_boss_greebles import lamps, mast, rect
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset
from game.view.bosses.world_2.fjord_lynx_frost import (
    icicles,
    snow_cap,
    spread,
)
from game.view.bosses.world_2.harbour_kraken_armour import (
    FORECASTLE_TOP,
    HEAD_SPAN,
    back_armour,
    shell_section,
    vein,
    wings_armour,
)
from game.view.bosses.world_2.harbour_kraken_cargo import container_bay
from game.view.bosses.world_2.harbour_kraken_cranes import (
    DECK_Y,
    ORANGE_NEON,
    crane_limbs,
    grab,
    pedestal,
)
from game.view.bosses.world_2.w2_organic import (
    ICE_FLESH,
    fringe,
)
from game.view.enemies.enemy_shapes import HULL_SECTION, SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts

# __pragma__ ("noskip")


# The hull seen from above (right half, bow to stern).
HULL = mirrored([
    [0, 78],
    [10, 72],
    [22, 56],
    [28, 36],
    [30, 10],
    [30, -40],
    [27, -58],
    [18, -66],
    [0, -66],
])
# Heights of the hull: its keel, its rim, its deck.
HULL_Y = [-7.0, -1.0, DECK_Y]
# The bridge tower amidships (loft stations along Z: z, half width, bottom, top).
BRIDGE = [
    [HEAD_SPAN[0], 15, DECK_Y, 15],
    [6, 16, DECK_Y, 18],
    [14, 13, DECK_Y, 17],
    [HEAD_SPAN[1], 9, DECK_Y, 13],
]
# The laser emitter's lens (a lathe profile along its axis), at the bow.
LENS = [
    [0.0, 0.0],
    [4.0, 1.2],
    [3.4, 3.4],
    [0.0, 4.4],
]
# Where the emitter's barrel starts, and the twin guns' barrels.
EMITTER = [0.0, 6.0, 68.0]
GUNS = [9.0, 9.5, 58.0]


def draw_hull(p: EnemyParts) -> None:
    """Draw the mantle, its orange-lit rim and the shell under the head.

    Frost and icicles along its sides (FB-HARBOUR-KRAKEN-05). The shell's fore and aft sections and
    the forecastle are its armour (`harbour_kraken_armour`).
    """
    flesh = p.flesh
    neon = p.neon
    # FB-HARBOUR-KRAKEN-02: the mantle of a great kraken, cold dark flesh under a ridged shell.
    flesh.bevel_slab(HULL, HULL_Y, [3, 2], ICE_FLESH.slate, None, ICE_FLESH.graphite)
    shell_section(p, HEAD_SPAN[0], HEAD_SPAN[1])
    vein(p, 1)
    for s in SIDES:
        edge_strips(
            neon,
            [
                [s * 29.4, 28],
                [s * 29.6, 10],
                [s * 29.6, -40],
            ],
            0.8,
            [DECK_Y - 2, DECK_Y - 1],
            ORANGE_NEON,
        )
        fringe(flesh, [s * 29, -2, -30], [s, -0.3], 3, 9, ICE_FLESH.slate)
        icicles(flesh, spread([s * 30.5, -1, 20], [s * 30.5, -1, -50], 7), 5)
        icicles(flesh, spread([s * 21, -1, 58], [s * 11, -1, 71], 3), 4)


def draw_bridge(p: EnemyParts) -> None:
    """Draw the bridge tower.

    A lofted block, dark windows lit as it charges, a funnel and a mast.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    # The head amidships, its great eyes across its brow.
    flesh.loft(HULL_SECTION, BRIDGE, ICE_FLESH.graphite, None, None)
    snow_cap(flesh, rect(16, 12), 17, Placement([0, 0, -1]))
    flesh.box([22, 2.4, 1], ICE_FLESH.seam, Placement([0, 13.4, 15.6], 0, 0.4))
    for s in SIDES:
        organ(p.vein, 2.2, 6, ORANGE_NEON, Placement([s * 11, 12, 12]), 0.6)
    charge.box([18, 1, 0.6], WHITE, Placement([0, 14, 16.4], 0, 0.4))
    flesh.cylinder(4.5, 9, 6, ICE_FLESH.sinew, Placement([-6, 16, -9]), 3)
    neon.ring(4.4, 1.2, 8, ORANGE_NEON, Placement([-6, 22, -9]))
    hull.cylinder(3.6, 0.5, 8, SHADE["soot"], Placement([-6, 25, -9]))
    mast(p, [7, 17, -4], 9, ORANGE_NEON)
    lamps(neon, [[16, 9, 12]], 1.6, [1, 0.1, 0.12])
    lamps(neon, [[-16, 9, 12]], 1.6, [0.2, 1, 0.35])


def draw_bow(p: EnemyParts) -> None:
    """Draw the bow (FB-HARBOUR-KRAKEN-03).

    The laser emitter, its neon rings, and the twin guns either side of it, their mounts standing
    from the mantle (through the forecastle while it is on).
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    # The beak, a metal emitter grafted in it.
    organ(
        p.flesh,
        6,
        6,
        ICE_FLESH.bone,
        Placement(offset(EMITTER, 0, 0, -6), 0, QUARTER),
        0.6,
    )
    hull.cylinder(5, 6, 8, H.dark, Placement(EMITTER, 0, QUARTER), 4.2)
    neon.ring(5.1, 1, 8, ORANGE_NEON, Placement(offset(EMITTER, 0, 0, 2), 0, QUARTER))
    charge.lathe(LENS, 8, WHITE, Placement(offset(EMITTER, 0, 0, 6), 0, QUARTER))
    p.muzzle(offset(EMITTER, 0, 0, 10.4), "laser")
    foot = DECK_Y - 0.2
    for s in SIDES:
        hull.box(
            [5, FORECASTLE_TOP + 3 - foot, 6],
            H.panel,
            Placement([s * GUNS[0], foot, GUNS[2] - 2]),
            H.base,
        )
        barrels(p, [s * GUNS[0], GUNS[1], GUNS[2]], [1, 0], [1.2, 8])


def draw_stern(p: EnemyParts) -> None:
    """Draw the stern: the reactors and the hull's rudder fins."""
    for s in SIDES:
        reactor_sac(p, [s * 12, 1.5, -66], 4, ORANGE_NEON, ICE_FLESH.graphite)
        p.flesh.box([1.4, 6, 8], ICE_FLESH.sinew, Placement([s * 21, -6, -62]))
    reactor_sac(p, [0, 1.5, -66], 3, ORANGE_NEON, ICE_FLESH.slate)


def draw_core(p: EnemyParts) -> None:
    """Draw the core body: hull, bridge, bow, stern, and the crane pedestals."""
    draw_hull(p)
    draw_bridge(p)
    draw_bow(p)
    draw_stern(p)
    for end in ["fore", "aft"]:
        first = [0, 0]
        if len(CRANE_REST[end]) > 0:
            first = CRANE_REST[end][0]
        for s in SIDES:
            pedestal(p, offset(boss_point(s * first[0], first[1]), 0, DECK_Y, 0))


def boss_drawing(core: Any, parts: Any, limbs: Any, armour: Any) -> Any:
    """Return the `BossDrawing` of a boss model: what the model is drawn from."""
    return record({
        "core": core,
        "parts": parts,
        "turrets": None,
        "limbs": limbs,
        "ring": None,
        "armour": armour,
    })


def build_harbour_kraken(scene: Any) -> BuiltEnemyModel:
    """FB-HARBOUR-KRAKEN-01, FB-HARBOUR-KRAKEN-04: the Harbour Kraken.

    A cargo crane-ship with four crane arms swinging at the shoulder and the elbow, a grab cannon
    hanging from each, orange neon, frost over its deck.

    FB-HARBOUR-KRAKEN-02: now a living kraken, a shelled mantle of cold flesh with a head and beak
    amidships, four tentacles ending in clawed gun-fists, a brood sac of eggs at its stern.
    FB-HARBOUR-KRAKEN-07: its shell's fore and aft sections are armour of their own.
    """
    parts = record({
        "crane-fore-left": grab,
        "crane-fore-right": grab,
        "crane-aft-left": grab,
        "crane-aft-right": grab,
        "container-bay": container_bay,
    })
    armour = record({"back": {"whole": back_armour}, "wings": {"whole": wings_armour}})
    return build_boss_model(
        HARBOUR_KRAKEN,
        scene,
        ORANGE_NEON,
        boss_drawing(draw_core, parts, crane_limbs(), armour),
    )
