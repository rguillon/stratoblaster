# Copyright (c) 2026 Renaud Guillon
"""The Boreal Citadel's details (FB-BOREAL-CITADEL-02, 2-5).

Armour skirts on its deck's sides, snow drifts, dishes and masts, lamps along its avenue, buttresses
round its keep, heating pipes, the engine block's grilles and fins, the gun deck and the missile
hatches. Each drawing takes the `Zone`
of the deck it draws (what stands on its armour is drawn with the armour, FB-BOREAL-CITADEL-08).
Model space: logical pixels, nose +Z, Y up.
"""

import math

from game.config.bosses.world_2.boreal_citadel import BOREAL_GUNS, BOREAL_HATCHES, BOREAL_LENS
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import dish, grille, mast, rod, studs
from game.view.bosses.world_2.boreal_citadel_city import (
    AURORA,
    CITADEL_DECK,
    FROST,
    VIOLET,
    Zone,
    in_zone,
    rect,
)
from game.view.bosses.world_2.w2_organic import ICE_FLESH, sinew
from game.view.enemies.enemy_shapes import SIDES, decal
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING

from game.view.enemies.enemy_mesh import EnemyParts

if TYPE_CHECKING:
    from render.geometry.outline import OutlinePoint
type Vec3 = list[float]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
WHITE = [1.0, 1.0, 1.0]
QUARTER = math.pi / 2
# The gun deck on the keep's front, and the laser lens between its cannons.
GUN_DECK = rect(22.0, 16.0, [0.0, 34.0])
GUN_DECK_TOP = 21.0
LENS = [
    [0.0, 0.0],
    [3.2, 1.0],
    [2.0, 3.0],
    [0.0, 3.6],
]

# The armour skirts along the right side of the deck (+X), between the bow and the outrigger.
SKIRTS = [  # type: list[list[list[float]]]
    [
        [52, 52],
        [57.5, 42],
        [55, 40],
        [49.5, 50],
    ],
    [
        [58.5, 34],
        [60.5, 28],
        [58, 27.5],
        [56, 33],
    ],
]
# Snow drifts on the deck (right half): where, and how wide.
DRIFTS = [  # type: list[list[float]]
    [46, -16, 4.5],
    [14, -76, 4],
    [44, 34, 3.5],
    [27, 72, 3.5],
]
# A drift's mound (lathe profile, in units of its width).
DRIFT = [  # type: list[list[float]]
    [1, 0],
    [0.75, 0.25],
    [0.35, 0.42],
    [0, 0.45],
]
# The keep's buttresses (around it at these turns from the nose, mirrored), and their size.
BUTTRESSES = [math.pi / 4, (3 * math.pi) / 4]
BUTTRESS = [4, 13, 7]


def _draw_deck_edges(p: EnemyParts, zone: Zone) -> None:
    """Draw the deck's edges on `zone` (FB-BOREAL-CITADEL-06).

    Armour skirts lit by violet slits, and snow drifts piled on the deck.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    top = CITADEL_DECK.top
    for s in zone.sides:
        for skirt in SKIRTS:
            if not in_zone(zone, s * skirt[0][0], skirt[0][1]):
                continue
            outline: list[OutlinePoint] = [[s * q[0], q[1]] for q in skirt]
            hull.bevel_slab(
                outline,
                [top - 0.4, top, top + 2],
                [0, 0.8],
                H.panel,
                None,
                FROST.frosted,
            )
        if in_zone(zone, s * 55, 46):
            neon.box([0.5, 0.8, 9], VIOLET, Placement([s * 55, top + 1.2, 46], s * 0.5))
        for x, z, w in DRIFTS:
            if not in_zone(zone, s * x, z):
                continue
            mound: list[list[float]] = [[r * w, y * w] for r, y in DRIFT]
            flesh.lathe(mound, 6, ICE_FLESH.crystal, Placement([s * x, top, z], x))


def _draw_keep_detail(p: EnemyParts) -> None:
    """Buttresses round the keep, snowed on top, and heating pipes from the domes to the keep."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    top = CITADEL_DECK.top
    for s in SIDES:
        for a in BUTTRESSES:
            turn = s * a
            at: Vec3 = [math.sin(turn) * 21, top, math.cos(turn) * 21]
            flesh.box(BUTTRESS, ICE_FLESH.sinew, Placement(at, turn), ICE_FLESH.rime)
            neon.box(
                [0.4, 6, 0.4],
                AURORA if s > 0 else VIOLET,
                Placement(
                    [math.sin(turn) * 24.2, top + 3, math.cos(turn) * 24.2],
                    turn,
                ),
            )
        # Arteries from the blisters to the heart, a metal pipe grafted along them.
        sinew(flesh, [s * 30, top + 1, 32], [s * 17, top + 1, 15], 1.2, ICE_FLESH.slate)
        rod(hull, [s * 27, top + 1, 35], [s * 14, top + 1, 18], 0.6, H.dark)


def _draw_roofs(p: EnemyParts, zone: Zone) -> None:
    """Masts and dishes over the city on `zone` (FB-BOREAL-CITADEL-03), lamps along the avenue."""
    top = CITADEL_DECK.top
    avenue = CITADEL_DECK.avenue
    for s in zone.sides:
        if in_zone(zone, s * 50, 26):
            dish(p, [s * 50, top, 26], 4, [0.6, s * 0.8])
        if in_zone(zone, s * 36, 2):
            mast(p, [s * 36, top + 19, 2], 7, AURORA if s > 0 else VIOLET)
        if not in_zone(zone, s * 24, -24):
            continue
        mast(p, [s * 24, top + 25, -24], 8, VIOLET)
        studs(
            p.neon,
            [
                [s * 13, -60],
                [s * 13, -26],
            ],
            [6, 1.2],
            avenue + 0.05,
            AURORA,
        )


def _draw_engine_block(p: EnemyParts) -> None:
    """Draw the engine block's grilles and heat-sink fins."""
    hull = p.hull
    flesh = p.flesh
    for s in SIDES:
        grille(hull, [s * 19, -86], [10, 8], [4, 5.05])
        # On the block's top (the outermost one stood off its edge, BOSS-52).
        for dx in [3, 5, 7]:
            flesh.box(
                [1, 3, 9],
                ICE_FLESH.bone,
                Placement([s * (dx + 22), 5, -86]),
                ICE_FLESH.rime,
            )
    decal(hull, rect(8, 8, [0, -86]), 5.05, H.dark)


def draw_gun_deck(p: EnemyParts) -> None:
    """Draw the gun deck on the keep's front (FB-BOREAL-CITADEL-04).

    Twin cannons and a laser lens, charging to fire.
    """
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
    """Draw the missile hatches on the avenue behind the keep (FB-BOREAL-CITADEL-04).

    They are lit as missiles load.
    """
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


def draw_details(p: EnemyParts, zone: Zone) -> None:
    """Draw the Boreal Citadel's details (FB-BOREAL-CITADEL-02) on the `zone` of its deck."""
    _draw_deck_edges(p, zone)
    _draw_roofs(p, zone)
    if zone.name == "core":
        _draw_keep_detail(p)
        _draw_engine_block(p)
