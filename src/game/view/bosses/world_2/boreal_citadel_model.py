"""P08-R10, 2-5: the Boreal Citadel, World 2's last boss

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A polar city on
a flying hull: a snowed deck with towers and heated domes, an avenue down its middle carrying
the keep, outriggers out to the aurora cannons.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_2.boreal_citadel import (
    BOREAL_CITADEL,
    BOREAL_GUNS,
    BOREAL_HATCHES,
    BOREAL_LENS,
    BOREAL_SPIRE,
)
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.record import record
from game.view.enemies.enemy_shapes import SIDES, decal, flip_x  # noqa: E402
from game.view.enemies.organic_parts import reactor_sac  # noqa: E402
from render.geometry.organic import RibSpec, ribs  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

__pragma__("noskip")

from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.overlord_city import edge_lights, symmetric  # noqa: E402
from game.view.bosses.world_2.boreal_citadel_city import (  # noqa: E402
    AURORA,
    CITADEL_DECK,
    VIOLET,
    draw_city,
    icicles,
    rect,
)
from game.view.bosses.world_2.boreal_citadel_details import draw_details  # noqa: E402
from game.view.bosses.world_2.boreal_citadel_parts import (  # noqa: E402
    OUTRIGGER_TOP,
    draw_battery,
    draw_cannon,
    draw_cannon_mount,
    draw_dome,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    glow_vein,
    sinew,
)

H = ENEMY_LOOK.hull
WHITE = [1.0, 1.0, 1.0]
QUARTER = math.pi / 2

# The deck (right half, front to tail), the avenue on it, and the right outrigger.
DECK = symmetric(
    [
        [20.0, 84.0],
        [44.0, 66.0],
        [60.0, 36.0],
        [62.0, -20.0],
        [54.0, -56.0],
        [36.0, -78.0],
        [18.0, -84.0],
    ],
    86,
)
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
# The gun deck on the keep's front, and the laser lens between its cannons.
GUN_DECK = rect(22.0, 16.0, [0.0, 34.0])
GUN_DECK_TOP = 21.0
LENS = [
    [0.0, 0.0],
    [3.2, 1.0],
    [2.0, 3.0],
    [0.0, 3.6],
]


def draw_hull(p: EnemyParts) -> None:
    """The deck with its snow and lit rim, the avenue, the engine block, the outriggers."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    top = CITADEL_DECK.top
    avenue = CITADEL_DECK.avenue
    # P16-R06: the back of a colossal beast, rimed flesh, its spine (the avenue) a ridge of bone.
    flesh.bevel_slab(DECK, [-8.0, -2.0, top], [3.0, 3.0], ICE_FLESH.teal, None, ICE_FLESH.rime)
    edge_lights(
        neon,
        DECK,
        [i for i in range(len(DECK))],
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
    for s in SIDES:
        wing = OUTRIGGER if s > 0 else flip_x(OUTRIGGER)
        flesh.bevel_slab(
            wing,
            [-4.0, -1.0, OUTRIGGER_TOP],
            [1.0, 2.0],
            ICE_FLESH.membrane,
            None,
            ICE_FLESH.purple,
        )
        sinew(
            flesh,
            [s * 58.0, OUTRIGGER_TOP, 0.0],
            [s * 98.0, OUTRIGGER_TOP, 2.0],
            1.6,
            ICE_FLESH.bone,
            [0.0, 1.0, 6.0],
        )
        glow_vein(p, [s * 18.0, top + 1.0, 40.0], [s * 56.0, top, 0.0], 1.4, AURORA)
        edge_lights(neon, wing, [0, 1, 2], [-1.5, -0.5], AURORA)
        icicles(flesh, [wing[0], wing[1]], -1, 5)
        for edge in BOW_EDGES:
            a = edge[0]
            b = edge[1]
            pair: list[OutlinePoint] = [[s * a[0], a[1]], [s * b[0], b[1]]]
            icicles(flesh, pair, -2, 4)


def draw_keep(p: EnemyParts) -> None:
    """The keep over the core: tiers lit green and violet, its spire and ring emitter on top."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    base = CITADEL_DECK.top
    # P16-R06: the keep is the beast's heart, a stepped mound of flesh, metal bands on its ledges.
    flesh.lathe(KEEP, 8, ICE_FLESH.purple, Placement([0.0, base, 0.0], math.pi / 8))
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


def draw_gun_deck(p: EnemyParts) -> None:
    """The gun deck on the keep's front: twin cannons and a laser lens, charging to fire."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    base = CITADEL_DECK.top
    hull.bevel_slab(GUN_DECK, [base, base, GUN_DECK_TOP], [0.0, 1.5], H.base, None, H.panel)
    decal(neon, rect(16.0, 1.2, [0.0, 39.0]), GUN_DECK_TOP + 0.05, VIOLET)
    front = 42.0
    for m in BOREAL_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        hull.cylinder(
            1.7,
            tip[2] - 2.0 - (front - 6.0),
            6,
            H.dark,
            Placement([tip[0], tip[1], front - 6.0], 0.0, QUARTER),
            1.4,
        )
        charge.cylinder(
            1.6,
            2.0,
            6,
            WHITE,
            Placement([tip[0], tip[1], tip[2] - 2.0], 0.0, QUARTER),
            1.1,
        )
        muzzle(tip)
    lens = boss_point(BOREAL_LENS[0], BOREAL_LENS[1], BOREAL_LENS[2])
    lens_at = lens[2] - LENS[3][1]
    hull.cylinder(
        4.0,
        lens_at - (front - 4.0),
        8,
        H.dark,
        Placement([0.0, lens[1], front - 4.0], 0.0, QUARTER),
    )
    charge.lathe(LENS, 6, WHITE, Placement([0.0, lens[1], lens_at], 0.0, QUARTER))
    muzzle(lens, "laser")


def draw_hatches(p: EnemyParts) -> None:
    """The missile hatches on the avenue behind the keep, lit as missiles load."""
    hull = p.hull
    charge = p.charge
    muzzle = p.muzzle
    for m in BOREAL_HATCHES:
        at = boss_point(m[0], m[1], m[2])
        x = at[0]
        y = at[1]
        z = at[2]
        decal(hull, rect(6.4, 5.4, [x, z]), y - 0.06, H.dark)
        decal(charge, rect(4.6, 3.6, [x, z]), y, WHITE)
        muzzle([x, y, z], "missile")


def draw_core(parts: EnemyParts) -> None:
    """The core: hull, city, keep, gun deck and hatches, four reactors in the engine block."""
    draw_hull(parts)
    draw_city(parts)
    draw_keep(parts)
    draw_gun_deck(parts)
    draw_hatches(parts)
    draw_details(parts)
    for s in SIDES:
        reactor_sac(parts, [s * 12.0, -1.0, -92.0], 5.5, AURORA, ICE_FLESH.purple, 8)
        reactor_sac(parts, [s * 26.0, -1.0, -92.0], 4.2, AURORA, ICE_FLESH.crimson, 6)


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """What `build_boss_model` draws a boss from."""
    return record({"core": core, "parts": parts, "turrets": turrets, "limbs": limbs, "ring": ring})


def build_boreal_citadel(scene: Any) -> BuiltEnemyModel:
    """P08-R10: the Boreal Citadel, the polar city's flying fortress (6 L) under aurora green and
    violet neon: towers and heated domes on a snowed deck, two aurora cannons on its outriggers,
    two missile batteries aft, two dome generators ahead, and a keep over the core carrying a
    laser, twin cannons, a ring emitter and missile hatches.
    P16-R06: now a colossal living beast carrying its city on its back: rimed flesh, a spine of
    bone, spires of crystal and flesh where the towers were, its heart (the keep) banded in metal,
    membrane fins out to its cannons, glowing blisters for domes."""
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
            None,
            None,
        ),
    )
    return model
