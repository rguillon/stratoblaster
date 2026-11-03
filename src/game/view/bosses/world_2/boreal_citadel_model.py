# Copyright (c) 2026 Renaud Guillon
"""FB-BOREAL-CITADEL-01 to FB-BOREAL-CITADEL-07, 2-5: the Boreal Citadel, World 2's last boss.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A polar city on
a flying hull: a snowed deck with towers and heated domes, an avenue down its middle carrying
the keep, outriggers out to the aurora cannons. Its bow doors and wing panels are armour drawn apart
(`boreal_citadel_armour`, D-254): the core's deck is drawn without them.
"""

import math

from game.config.bosses.world_2.boreal_citadel import BOREAL_CITADEL, BOREAL_SPIRE
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.overlord_city import edge_lights
from game.view.bosses.world_2.boreal_citadel_armour import (
    DECK,
    DECK_BOTTOM,
    DECK_SLOPE,
    DECK_WAIST,
    HOLD,
    citadel_armour,
    draw_core_panels,
)
from game.view.bosses.world_2.boreal_citadel_city import (
    AURORA,
    CITADEL_DECK,
    CORE,
    VIOLET,
    draw_city,
    icicles,
    rect,
)
from game.view.bosses.world_2.boreal_citadel_details import (
    draw_details,
    draw_gun_deck,
    draw_hatches,
)
from game.view.bosses.world_2.boreal_citadel_parts import (
    OUTRIGGER_TOP,
    draw_battery,
    draw_cannon,
    draw_cannon_mount,
    draw_dome,
)
from game.view.bosses.world_2.w2_organic import ICE_FLESH, sinew
from game.view.enemies.enemy_shapes import SIDES, flip_x
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import RibSpec, ribs
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING, Any

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts

if TYPE_CHECKING:
    from render.geometry.outline import OutlinePoint
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
WHITE = [1.0, 1.0, 1.0]
QUARTER = math.pi / 2

# The avenue on the deck (`DECK`), and the right outrigger.
AVENUE = rect(32.0, 94.0, [0.0, -17.0])
OUTRIGGER = [
    [56.0, 26.0],
    [94.0, 18.0],
    [100.0, 10.0],
    [100.0, -6.0],
    [94.0, -14.0],
    [56.0, -24.0],
]
# The deck's bow edges (right half), icicles hanging under them.
BOW_EDGES = [
    [
        [20.0, 84.0],
        [44.0, 66.0],
    ],
    [
        [44.0, 66.0],
        [60.0, 36.0],
    ],
]
# The engine block across the tail.
ENGINES = rect(62.0, 12.0, [0.0, -86.0])

# The keep over the core: a stepped octagonal tower (lathe profile, bottom to top) and its spire.
KEEP = [
    [22.0, 0.0],
    [21.5, 12.0],
    [17.0, 14.0],
    [16.5, 21.0],
    [11.0, 23.0],
    [10.5, 28.0],
    [6.0, 30.0],
    [0.0, 30.5],
]
# The keep's ledges (from the profile's outer to its inner edge), snowed over, and the radius of
# the lit band round the wall under each.
LEDGES = [
    ([21.5, 12.0], [17.0, 14.0], AURORA, 21.8),
    ([16.5, 21.0], [11.0, 23.0], VIOLET, 16.9),
    ([10.5, 28.0], [6.0, 30.0], AURORA, 11.0),
]
SPIRE = [
    [3.5, 0.0],
    [2.4, 5.0],
    [1.2, 7.0],
]
SPIRE_TIP = [
    [1.4, 0.0],
    [0.0, 2.0],
]


def draw_hull(p: EnemyParts) -> None:
    """Draw the deck with its snow and lit rim, the avenue, the engine block, the outriggers."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    top = CITADEL_DECK.top
    avenue = CITADEL_DECK.avenue
    # FB-BOREAL-CITADEL-02: the back of a colossal beast, rimed flesh, its spine (the avenue) a
    # ridge of bone. Its flesh up to the hold, the panels no armour holds over it (FB-BOREAL-
    # CITADEL-08: the bow doors and wing panels are its armour, `citadel_armour`).
    flesh.bevel_slab(
        DECK,
        [DECK_BOTTOM, DECK_WAIST, HOLD],
        [3.0, (HOLD - DECK_WAIST) * DECK_SLOPE],
        ICE_FLESH.teal,
        None,
        ICE_FLESH.graphite,
    )
    draw_core_panels(p, SIDES)
    edge_lights(
        neon,
        DECK,
        list(range(len(DECK))),
        [-2.6, -1.4],
        AURORA,
    )
    flesh.bevel_slab(
        AVENUE,
        [top - 1.0, top, avenue],
        [0.0, 3.0],
        ICE_FLESH.bone,
        None,
        ICE_FLESH.sinew,
    )
    ribs(
        flesh,
        [-60.0, -48.0, -36.0],
        RibSpec(17.0, top, 8.0, 1.1),
        ICE_FLESH.bone,
    )
    edge_lights(neon, AVENUE, [1, 3], [top + 0.4, top + 1.4], VIOLET)
    hull.bevel_slab(ENGINES, [-7.0, -1.0, 5.0], [1.0, 1.5], H.dark, None, H.base)
    draw_outriggers(p)


def draw_outriggers(p: EnemyParts) -> None:
    """Draw the outriggers with their sinews, lit edges and icicles, and the bow's icicles."""
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        wing = OUTRIGGER if s > 0 else flip_x(OUTRIGGER)
        flesh.bevel_slab(
            wing,
            [-4.0, -1.0, OUTRIGGER_TOP],
            [1.0, 2.0],
            ICE_FLESH.membrane,
            None,
            ICE_FLESH.graphite,
        )
        sinew(
            flesh,
            [s * 58.0, OUTRIGGER_TOP, 0.0],
            [s * 98.0, OUTRIGGER_TOP, 2.0],
            1.6,
            ICE_FLESH.bone,
            [0.0, 1.0, 6.0],
        )
        edge_lights(neon, wing, [0, 1, 2], [-1.5, -0.5], AURORA)
        icicles(flesh, [wing[0], wing[1]], -1, 5)
        for edge in BOW_EDGES:
            a = edge[0]
            b = edge[1]
            pair: list[OutlinePoint] = [[s * a[0], a[1]], [s * b[0], b[1]]]
            icicles(flesh, pair, -2, 4)


def draw_keep(p: EnemyParts) -> None:
    """Draw the keep over the core.

    Tiers lit green and violet, its spire and ring emitter on top.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    base = CITADEL_DECK.top
    # FB-BOREAL-CITADEL-02: the keep is the beast's heart, a stepped mound of flesh, metal bands on
    # its ledges.
    flesh.lathe(KEEP, 8, ICE_FLESH.graphite, Placement([0.0, base, 0.0], math.pi / 8))
    for ledge in LEDGES:
        inner = ledge[0]
        outer = ledge[1]
        color = ledge[2]
        lit = ledge[3]
        hull.lathe(
            [
                [inner[0] + 0.2, inner[1] + 0.05],
                [outer[0] + 0.1, outer[1] + 0.1],
            ],
            8,
            H.panel,
            Placement([0.0, base, 0.0], math.pi / 8),
            False,
        )
        neon.ring(lit, 1.1, 8, color, Placement([0.0, base + inner[1] - 2.6, 0.0], math.pi / 8))
    spire = base + 30.0
    flesh.lathe(SPIRE, 6, ICE_FLESH.crystal, Placement([0.0, spire, 0.0]))
    charge.lathe(SPIRE_TIP, 6, WHITE, Placement([0.0, spire + 7.0, 0.0]))
    muzzle(boss_point(BOREAL_SPIRE[0], BOREAL_SPIRE[1], BOREAL_SPIRE[2]), "ring")


def draw_core(parts: EnemyParts) -> None:
    """Draw the core: hull, city, keep, gun deck and hatches, four reactors in the engine block."""
    draw_hull(parts)
    draw_city(parts, CORE)
    draw_keep(parts)
    draw_gun_deck(parts)
    draw_hatches(parts)
    draw_details(parts, CORE)
    for s in SIDES:
        reactor_sac(parts, [s * 12.0, -1.0, -92.0], 5.5, AURORA, ICE_FLESH.graphite, 8)
        reactor_sac(parts, [s * 26.0, -1.0, -92.0], 4.2, AURORA, ICE_FLESH.slate, 6)


def boss_drawing(core: Any, parts: Any, turrets: Any, armour: Any) -> Any:
    """Return what `build_boss_model` draws a boss from."""
    return record({
        "core": core,
        "parts": parts,
        "turrets": turrets,
        "limbs": None,
        "ring": None,
        "armour": armour,
    })


def build_boreal_citadel(scene: Any) -> BuiltEnemyModel:
    """FB-BOREAL-CITADEL-01, FB-BOREAL-CITADEL-05: the Boreal Citadel.

    The polar city's flying fortress (6 L) under aurora green and violet neon: towers and heated
    domes on a snowed deck, two aurora cannons on its outriggers, two missile batteries aft, two
    dome generators ahead, and a keep over the core carrying a laser, twin cannons, a ring emitter
    and missile hatches.
    FB-BOREAL-CITADEL-02, FB-BOREAL-CITADEL-03: now a colossal living beast carrying its city on
    its back: rimed flesh, a spine of bone, spires of crystal and flesh where the towers were, its
    heart (the keep) banded in metal, membrane fins out to its cannons, glowing blisters for domes.
    FB-BOREAL-CITADEL-08: its bow doors and wing panels, with what stands on them, are its armour.
    """
    model: BuiltEnemyModel = build_boss_model(
        BOREAL_CITADEL,
        scene,
        AURORA,
        boss_drawing(
            draw_core,
            {
                "cannon-left": draw_cannon_mount,
                "cannon-right": draw_cannon_mount,
                "battery-left": draw_battery,
                "battery-right": draw_battery,
                "dome-left": draw_dome,
                "dome-right": draw_dome,
            },
            {"cannon-left": draw_cannon, "cannon-right": draw_cannon},
            citadel_armour(),
        ),
    )
    return model
