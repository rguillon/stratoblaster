"""The Glacier Colossus (P08-R10, 2-4), ported from `bosses/world-2/glacier-colossus-model.ts`.

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_2.glacier_colossus import (
    COLOSSUS_CORE_GUNS,
    COLOSSUS_STACK,
    GLACIER_COLOSSUS,
)
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_shapes import mirrored
from game.view.bosses.mini_boss_greebles import lamps, mast, plate, rect, vent
from game.view.bosses.mini_boss_shapes import SHADE, WHITE, H, neon_band, offset, scaled
from game.view.bosses.world_2.avalanche_frost import (  # noqa: E402
    FROST,
    PACKED,
    barrel_to,
    icicles,
    snow_cap,
)
from game.view.bosses.world_2.glacier_colossus_parts import (  # noqa: E402
    COLOSSUS_NEON,
    cutter,
    cutter_mount,
    heat_sink,
    missile_pod,
    ore_cannon,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    glow_vein,
    shell,
    spine_row,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import RibSpec, SegmentedBody, ribs
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts  # noqa: E402

__pragma__("noskip")

N = COLOSSUS_NEON

# The hull seen from above (its right half, bow to stern): a broad, blunt mining ship.
HULL = mirrored(
    [
        [0, 62],
        [22, 58],
        [46, 44],
        [60, 22],
        [64, -6],
        [60, -40],
        [46, -66],
        [22, -78],
        [0, -78],
    ]
)
# Heights of the hull: its keel, its waist (the widest), its deck.
HULL_Y = [-8.0, 0.0, 10.0]
# The raised upper deck along the middle.
UPPER = mirrored(
    [
        [0, 40],
        [18, 38],
        [30, 24],
        [32, -30],
        [24, -56],
        [0, -60],
    ]
)
UPPER_Y = [10.0, 11.0, 16.0]
# The bridge tower on the upper deck, ahead of the heat stack.
TOWER = [  # type: list[list[float]]
    [-15.0, 8.0],
    [15.0, 8.0],
    [15.0, 24.0],
    [10.0, 28.0],
    [-10.0, 28.0],
    [-15.0, 24.0],
]
TOWER_Y = [16.0, 18.0, 28.0]
# The heat vents along each side of the deck (centres along Z, on the right at +X).
VENTS_Z = [-40, -26, -12, 2]
VENT_X = 45

# A weathered patch welded on the upper deck's right.
PATCH = [  # type: list[list[float]]
    [-26.0, -20.0],
    [-18.0, -20.0],
    [-18.0, -6.0],
    [-27.0, -8.0],
]


def snow_caps() -> list[Any]:
    """Snow caps on the decks and the tower's roof: outline, height, colour."""
    return [
        [
            [
                [20, 44],
                [40, 40],
                [44, 30],
                [26, 36],
            ],
            HULL_Y[2],
            FROST,
        ],
        [
            [
                [-22, 50],
                [-36, 44],
                [-48, 34],
                [-30, 36],
            ],
            HULL_Y[2],
            FROST,
        ],
        [
            [
                [-50, 6],
                [-58, -6],
                [-56, -30],
                [-50, -24],
            ],
            HULL_Y[2],
            FROST,
        ],
        [
            [
                [48, -46],
                [56, -44],
                [54, -58],
                [48, -60],
            ],
            HULL_Y[2],
            FROST,
        ],
        [
            [
                [-12, 10],
                [12, 10],
                [10, 18],
                [-8, 20],
            ],
            TOWER_Y[2],
            FROST,
        ],
        [
            [
                [10, -30],
                [26, -28],
                [24, -48],
                [12, -50],
            ],
            UPPER_Y[2],
            PACKED,
        ],
    ]


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """The `BossDrawing` of a boss model (`boss-model.ts`): what the model is drawn from."""
    return record({"core": core, "parts": parts, "turrets": turrets, "limbs": limbs, "ring": ring})


def draw_hull(p: EnemyParts) -> None:
    """The hull, its neon band, the upper deck and the bridge tower."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a glacier titan, a vast body of cold flesh under a ridged shell, its brain hump
    # where the bridge tower was, eyes round it.
    flesh.bevel_slab(HULL, HULL_Y, [3, 2.5], ICE_FLESH.sinew, None, ICE_FLESH.teal)
    neon_band(neon, HULL, [-3.6, -1.2], [0.985, 1.015], N)
    flesh.bevel_slab(UPPER, UPPER_Y, [0, 1.6], ICE_FLESH.teal, None, ICE_FLESH.purple)
    shell(
        flesh,
        SegmentedBody(-58, 6, 5, 26, UPPER_Y[2] - 1, 24),
        ICE_FLESH.teal,
    )
    flesh.bevel_slab(TOWER, TOWER_Y, [0, 4], ICE_FLESH.purple, None, ICE_FLESH.rime)
    neon_band(flesh, TOWER, [22, 24.5], [1.02, 1.02], ICE_FLESH.seam)
    eyes(p, [0, 23, 28.4], record({"count": 4, "size": 1.2, "spacing": 5}), N)
    neon_band(neon, TOWER, [25, 25.8], [1.02, 1.02], N)
    for tip in COLOSSUS_CORE_GUNS:
        barrel_to(p, tip, [2, 8])
    for s in SIDES:
        # The pylons out to the cutters (they stay when a cutter is gone).
        flesh.box([16, 5, 12], ICE_FLESH.sinew, Placement([s * 64, 1, 10]), ICE_FLESH.rime)
        hull.box([6, 6, 13], H.panel, Placement([s * 60, 1, 10]), H.base)
        reactor_sac(p, [s * 16, 2, -78], 5, N, ICE_FLESH.purple)
        p.reactor([s * 38, 2, -70], 4.5)


def draw_stack(p: EnemyParts) -> None:
    """The heat stack behind the tower, glowing at its top: the core's rings leave from there."""
    if len(COLOSSUS_STACK) == 0:
        return
    ring = COLOSSUS_STACK[0]
    top = boss_point(ring[0], ring[1], ring[2])
    foot = offset(top, 0, -16, 0)
    # A spiracle of flesh breathing heat, a metal ring grafted round its mouth.
    p.flesh.cylinder(9, 13, 7, ICE_FLESH.crimson, Placement(foot, math.pi / 8), 7)
    p.hull.ring(7.9, 2, 8, H.panel, Placement(offset(foot, 0, 12, 0), math.pi / 8))
    p.neon.ring(7.8, 1.2, 8, N, Placement(offset(foot, 0, 10.5, 0), math.pi / 8))
    p.charge.cylinder(5.5, 3, 8, WHITE, Placement(offset(top, 0, -3, 0)), 2.5)
    p.muzzle(top, "ring")
    for s in SIDES:
        p.flesh.cylinder(3, 9, 5, ICE_FLESH.sinew, Placement(offset(foot, s * 12, 0, -4)), 2.4)
        p.hull.cylinder(2.7, 1, 6, SHADE["soot"], Placement(offset(foot, s * 12, 9, -4)))


def draw_vents(p: EnemyParts) -> None:
    """The heat vents along the deck: dark grilles glowing red-orange between their slats."""
    hull = p.hull
    neon = p.neon
    for s in SIDES:
        # Veins out from the shell to the rim; the vents are gill slits glowing between metal
        # grilles.
        for pair in [[20, 24], [-48, -54]]:
            glow_vein(
                p,
                [s * 30, HULL_Y[2] + 2, pair[0]],
                [s * 58, HULL_Y[2], pair[1]],
                1.3,
                N,
            )
        for z in VENTS_Z:
            at = [s * VENT_X, HULL_Y[2] - 0.2, z]
            neon.box([8, 0.5, 8.5], N, Placement(offset(at, 0, 0.1, 0)))
            vent(hull, at, [10, 10], 4)


def draw_frost(p: EnemyParts) -> None:
    """The frost: snow caps on the decks and the tower's roof, icicles under the hull's rim."""
    hull = p.flesh
    for item in snow_caps():
        snow_cap(hull, item[0], item[1], 1.2, item[2])
    rim = scaled(HULL, 0.95)
    icicles(hull, [[q[0], HULL_Y[0] + 1.5, q[1]] for q in rim], 6)


def draw_wear(p: EnemyParts) -> None:
    """Ore bins heaped with rock and snow on the stern, and wear: hazard paint, a patch, masts."""
    hull = p.hull
    flesh = p.flesh
    for s in SIDES:
        # Glacier ice grown through the flesh on the stern, crystals over the shell.
        crystals(flesh, [s * 38, HULL_Y[2], -57], 9, 4)
        crystals(flesh, [s * 20, UPPER_Y[2] + 4, -20], 5)
        ribs(flesh, [s * 46], RibSpec(4, HULL_Y[2], 3, 0.8), ICE_FLESH.bone)
        lamps(p.neon, [[s * 60, HULL_Y[2], -8]], 1.8, N)
    plate(hull, rect(18, 8), [HULL_Y[2], 1], H.panel, Placement([0, 0, 33]))
    plate(hull, PATCH, [UPPER_Y[2], 0.6], SHADE["patch"])
    spine_row(flesh, [0, 24, -6], [0, 22, -50], 5, 5)
    mast(p, [8, TOWER_Y[2], 12], 8, N)
    mast(p, [-24, UPPER_Y[2], -54], 6, N)


def draw_core(p: EnemyParts) -> None:
    """The core body: the hull, the stack, the vents, the frost and the wear."""
    draw_hull(p)
    draw_stack(p)
    draw_vents(p)
    draw_frost(p)
    draw_wear(p)


def build_glacier_colossus(scene: Any) -> BuiltEnemyModel:
    """P08-R10: the Glacier Colossus, a giant mining ship 5.5 L across, red-orange neon, glowing
    heat vents along its deck, crusted with snow and hung with icicles; its cutters out on its
    beam, its ore cannons and heat sink at its bow, its missile pod on its stern.
    P16-R06: now a living glacier titan, a vast shelled body of cold flesh with glacier ice grown
    through it, gills glowing down its back; its parts armoured organs and fleshy gun limbs.
    """
    parts = record(
        {
            "cutter-left": cutter_mount,
            "cutter-right": cutter_mount,
            "ore-left": ore_cannon,
            "ore-right": ore_cannon,
            "heat-sink": heat_sink,
            "missile-pod": missile_pod,
        }
    )
    turrets = record({"cutter-left": cutter, "cutter-right": cutter})
    return build_boss_model(
        GLACIER_COLOSSUS,
        scene,
        N,
        boss_drawing(draw_core, parts, turrets, None, None),
    )
