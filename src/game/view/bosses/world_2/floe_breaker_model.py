# Copyright (c) 2026 Renaud Guillon
"""MB-FLOE-BREAKER-01 to MB-FLOE-BREAKER-06, 2-1: the Floe Breaker.

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.world_2.floe_breaker import FLOE_BEACON, FLOE_BREAKER
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import barrels
from game.view.bosses.mini_boss_greebles import dish, lamps, mast
from game.view.bosses.mini_boss_shapes import (
    SHADE,
    WHITE,
    H,
    neon_band,
    offset,
    scaled,
    socket,
    turret,
)
from game.view.bosses.world_2.floe_breaker_armour import draw_plating
from game.view.bosses.world_2.floe_breaker_details import floe_dressing
from game.view.bosses.world_2.floe_breaker_frost import FROST
from game.view.bosses.world_2.w2_organic import (
    ICE_FLESH,
    crystals,
    fringe,
    gland,
    glow_vein,
    ice_teeth,
    shell,
    sinew,
    spine_row,
)
from game.view.enemies.enemy_shapes import SIDES, side_stripe
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import RibSpec, SegmentedBody, organ, ribs
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


# The navigation lights (cyan neon of the boss, from its look).
_CYAN_NEON = BOSS_LOOK.neon["floe-breaker"]
CYAN = _CYAN_NEON if _CYAN_NEON != None else [0.1, 0.85, 1.0]
# Navigation lights: red to port (+X, the screen's left), green to starboard.
PORT_RED = [1.0, 0.1, 0.12]
STARBOARD_GREEN = [0.2, 1.0, 0.35]

# The hover skirt seen from above: a long hull, sharp at the bow, square at the stern.
FLOE_HULL = [
    [0.0, 54.0],
    [9.0, 40.0],
    [19.0, 26.0],
    [29.0, 13.0],
    [35.0, 2.0],
    [36.0, -10.0],
    [35.0, -26.0],
    [30.0, -38.0],
    [18.0, -46.0],
    [-18.0, -46.0],
    [-30.0, -38.0],
    [-35.0, -26.0],
    [-36.0, -10.0],
    [-35.0, 2.0],
    [-29.0, 13.0],
    [-19.0, 26.0],
    [-9.0, 40.0],
]
# Heights of the skirt: its bottom, its rim (the widest), its deck.
SKIRT = [-5.0, -1.0, 3.0]
# The armoured bow: a ridged wedge of bone along the front deck, cutting through the floes. It is
# a keel the front plating lies either side of (MB-FLOE-BREAKER-07, `floe_breaker_armour`): the
# gatlings rise beside it once the plating is shed.
BOW_SECTION = [
    [1.0, 0.0],
    [0.8, 0.5],
    [0.3, 0.92],
    [0.0, 1.0],
    [-0.3, 0.92],
    [-0.8, 0.5],
    [-1.0, 0.0],
]
# Its loft stations (z, half width, bottom, top), aft to the point of the bow; its base lies on
# the deck.
BOW = [
    [4.0, 13.0, 3.0, 9.0],
    [20.0, 10.0, 3.0, 10.0],
    [36.0, 6.5, 2.5, 8.0],
    [49.0, 3.0, 1.5, 4.5],
    [56.0, 0.0, 2.5, 2.5],
]
# The ice-breaking blades grafted on the ram's flanks, `[z, x]`, and the height of their base.
BLADES = [[44.0, 4.3], [33.0, 6.7], [22.0, 8.9]]
BLADE_Y = 4.2
# The sponsons' mounting plate (an octagon, in units of the part's radius).
MOUNT = [
    [math.sin(2 * math.pi * (k + 0.5) / 8), math.cos(2 * math.pi * (k + 0.5) / 8)] for k in range(8)
]
# The frost beacon on the bridge roof: a lathe profile (the core's ring gun).
BEACON = [
    [3.6, 0.0],
    [3.8, 1.5],
    [2.6, 3.4],
    [0.0, 4.0],
]


def sign_of(x: float) -> float:
    """`Math.sign`: -1, 0 or 1."""
    if x > 0:
        return 1.0
    if x < 0:
        return -1.0
    return 0.0


# The bow's sides crusted with ice (its top facets, port and starboard).
BOW_ICE_SIDES = [2, 3]


def bow_paint(side: int, band: int) -> Any:
    """Return the bow's top facets crusted with ice on its front bands (None: the bow's own colour).

    MB-FLOE-BREAKER-05.
    """
    if side in BOW_ICE_SIDES and band >= 1:
        return FROST.snow
    return None


def draw_hull(p: EnemyParts) -> None:
    """Draw the swollen body: a belly of rimed flesh on the hull, a shelled back, a bone ram.

    The shell ends under the ram's base: the front deck either side of the ram carries the plating
    it sheds (`draw_plating`).
    """
    flesh = p.flesh
    neon = p.neon
    hull = p.hull
    # MB-FLOE-BREAKER-02: the old skirt is now the creature's belly, its cyan band a line of
    # photophores.
    flesh.bevel_slab(FLOE_HULL, SKIRT, [3.0, 3.0], ICE_FLESH.teal, None, ICE_FLESH.rime)
    neon_band(neon, FLOE_HULL, [-3.4, -1.1], [0.985, 1.02], CYAN)
    shell(flesh, SegmentedBody(-44.0, 8.0, 5, 27.0, 2.0, 11.0))
    flesh.loft(BOW_SECTION, BOW, ICE_FLESH.bone, None, LoftOptions(False, bow_paint))
    for side in [0, 5]:
        stripe = side_stripe(BOW_SECTION, side, [0.35, 0.8], 1.05)
        neon.loft(stripe, BOW[0:4], CYAN, None, LoftOptions(True))
    # The ice-breaking teeth: metal blades grafted along the ram's flanks, just over the plating.
    for s in SIDES:
        for station in BLADES:
            hull.box(
                [2.2, 2.4, 4.0],
                SHADE["edge"],
                Placement([s * station[1], BLADE_Y, station[0]], s * 0.6),
            )
        fringe(flesh, [s * 33.0, -2.0, -8.0], [s, -0.2], 3, 7)
    ice_teeth(flesh, FLOE_HULL, SKIRT[1], 3)


def draw_bridge(p: EnemyParts) -> None:
    """Draw the brain hump with its eyes and beacon gland, the spiracles and the hover fans aft.

    The fans spin (MB-FLOE-BREAKER-06).
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    organ(p.flesh, 13.0, 7, ICE_FLESH.graphite, Placement([0.0, 3.0, -18.0]), 0.5)
    ribs(
        p.flesh,
        [-26.0, -18.0, -10.0],
        RibSpec(13.0, 4.0, 9.0, 0.9),
        ICE_FLESH.bone,
    )
    # A row of eyes across the hump's brow, where the wheelhouse windows were.
    eyes(p, [0.0, 11.0, -7.5], {"count": 5, "size": 0.9, "spacing": 3}, CYAN)
    neon.box([22.0, 1.0, 0.4], CYAN, Placement([0.0, 7.6, -6.9]))
    hull.lathe(BEACON, 8, SHADE["edge"], Placement([0.0, 17.0, -18.0]))
    neon.ring(3.9, 0.5, 8, CYAN, Placement([0.0, 17.6, -18.0]))
    charge.cylinder(1.6, 2.4, 6, WHITE, Placement([0.0, 20.6, -18.0]), 0.6)
    for at in FLOE_BEACON:
        muzzle(boss_point(at[0], at[1], at[2]), "ring")
    for s in SIDES:
        # Spiracles breathing out of the back, a metal valve on each.
        p.flesh.cylinder(2.8, 9.0, 5, ICE_FLESH.sinew, Placement([s * 8.0, 4.0, -32.0]), 2.0)
        hull.cylinder(2.3, 0.6, 6, SHADE["soot"], Placement([s * 8.0, 13.0, -32.0]))
        p.flesh.ring(5.6, 2.0, 7, ICE_FLESH.graphite, Placement([s * 21.0, 3.6, -32.0]))
        p.rotor([s * 21.0, 4.4, -32.0], 4.6)
        reactor_sac(p, [s * 13.0, 0.5, -45.0], 3.2, CYAN, ICE_FLESH.graphite, 6)


def draw_deck(p: EnemyParts) -> None:
    """Back details: crystals, glands, veins, the ram's guns.

    The frosted plates and the crystals of the front deck are on its plating (`draw_plating`); the
    veins run from the hump down to the deck under it (they lie on the frame once it is shed).
    """
    hull = p.hull
    neon = p.neon
    for s in SIDES:
        glow_vein(p, [s * 6.0, 10.0, -10.0], [s * 22.0, 4.0, 10.0], 0.9, CYAN)
        gland(p, [s * 24.0, 4.0, -22.0], 1.4, CYAN)
    crystals(p.flesh, [-2.5, 8.0, 30.0], 2.5, 2)
    # An antenna stalk and a dish grafted on the hump, uneven (the mast rooted in the hump's flesh,
    # BOSS-52).
    dish(hull, [6.5, 17.0, -20.0], 3.2, -0.5, 0.4)
    mast(p, [-6.0, 14.0, -21.0], 6.0, CYAN)
    crystals(p.flesh, [22.0, 3.0, -40.0], 4)
    spine_row(p.flesh, [0.0, 9.0, -38.0], [0.0, 12.0, -30.0], 3, 3)
    lamps(neon, [[30.0, SKIRT[2], -30.0]], 1.6, PORT_RED)
    lamps(neon, [[-30.0, SKIRT[2], -30.0]], 1.6, STARBOARD_GREEN)
    # The ram's guns: a metal mount grafted on the bone, two short barrels (the core's fans).
    hull.box([8.0, 2.4, 6.0], H.dark, Placement([0.0, 9.2, 22.0]), H.panel)
    barrels(p, [0.0, 10.4, 25.0], [2, 6.0], [1.1, 6.0])


def draw_core(p: EnemyParts) -> None:
    """Draw the core: the hull, the bridge, the deck, the dressing and its sponsons' sockets."""
    draw_hull(p)
    draw_bridge(p)
    draw_deck(p)
    floe_dressing(p, CYAN)
    for s in SIDES:
        socket(p.hull, [s * 30.0, 3.0, 4.0], 8, 1.2)


def sponson(p: EnemyParts, at: Vec3) -> None:
    """Add a harpoon gun's sponson (MB-FLOE-BREAKER-03).

    A mounting plate on the beam and a cable reel outboard.
    """
    part = FLOE_BREAKER.stats.parts[0]
    # `parts[0]?.radius ?? 13`.
    r = 13.0 if part == None or part.radius == None else part.radius
    s = sign_of(at[0])
    # MB-FLOE-BREAKER-03: a muscle bulging out of the flank, a metal mount on top, the reel a gland.
    organ(p.flesh, r * 0.85, 7, ICE_FLESH.graphite, Placement(offset(at, 0.0, -2.0, 0.0)), 0.3)
    p.hull.bevel_slab(
        scaled(MOUNT, r * 0.55),
        [3.0, 3.8, 4.5],
        [0.4, 1.0],
        H.base,
        Placement(at),
        FROST.panel,
    )
    reel = offset(at, 10.0 if s > 0 else -10.0, 2.0, -6.0)
    organ(p.flesh, 3.4, 5, ICE_FLESH.sinew, Placement(reel, 0.0, 0.0, s * 0.8), 0.8)
    crystals(p.flesh, offset(at, s * 6.0, 3.0, 6.0), 3, 2)
    sinew(p.flesh, offset(at, -s * 8.0, 0.0, -4.0), offset(at, -s * 14.0, 1.0, -10.0), 1.6)
    # The light on its outer side, set in the muscle's flank (BOSS-52).
    p.neon.box([0.4, 1.2, 4.0], CYAN, Placement(offset(at, s * 10.4, 0.4, 3.0)))


def harpoon_turret(p: EnemyParts, at: Vec3) -> None:
    """Add a harpoon gun's turret (MB-FLOE-BREAKER-03): one long barrel, barbs near its tip."""
    top = offset(at, 0.0, 4.5, 0.0)
    turret(
        p,
        top,
        {
            "radius": 11,
            "barrels": 1,
            "gap": 0,
            "bore": 1.8,
            "length": 10,
            "neon": CYAN,
            "hatch": -sign_of(at[0]),
        },
    )
    for s in SIDES:
        p.hull.box(
            [0.5, 2.6, 2.6],
            SHADE["edge"],
            Placement(offset(top, s * 2.0, 1.8, 15.0), s * 0.5),
        )


def plating(p: EnemyParts) -> None:
    """Draw the `back` region's armour (MB-FLOE-BREAKER-07): the plating lying on the deck."""
    draw_plating(p, SKIRT[2])


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """Return what `build_boss_model` draws a boss from, with its `back` plating as its armour."""
    return record({
        "core": core,
        "parts": parts,
        "turrets": turrets,
        "limbs": limbs,
        "ring": ring,
        "armour": {"back": {"whole": plating}},
    })


def build_floe_breaker(scene: Any) -> BuiltEnemyModel:
    """MB-FLOE-BREAKER-01, MB-FLOE-BREAKER-04: the Floe Breaker, an icebreaker hovership.

    It has a sharp armoured bow, cyan neon around its skirt and along its bow; its two harpoon guns
    sit on sponsons either side.

    MB-FLOE-BREAKER-02: now a living ice-ram, a shelled sea beast with a bone ram, a brain hump and
    eyes, frost crystals grown through its flesh; its harpoons sit on muscles bulging from its
    flanks. The plating of its front deck is the armour it sheds (MB-FLOE-BREAKER-07).
    """
    model: BuiltEnemyModel = build_boss_model(
        FLOE_BREAKER,
        scene,
        CYAN,
        boss_drawing(
            draw_core,
            {"harpoon-left": sponson, "harpoon-right": sponson},
            {"harpoon-left": harpoon_turret, "harpoon-right": harpoon_turret},
            None,
            None,
        ),
    )
    return model
