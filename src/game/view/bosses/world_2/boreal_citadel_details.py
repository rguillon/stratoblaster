"""The Boreal Citadel's details (P08-R10, 2-5): armour skirts on its deck's sides, snow drifts,
dishes and masts, lamps along its avenue, buttresses round its keep, heating pipes, the engine
block's grilles and fins, ported from `bosses/world-2/boreal-citadel-details.ts`. Model space:
logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.final_boss_greebles import dish, grille, mast, rod, studs
from game.view.bosses.world_2.boreal_citadel_city import AURORA, CITADEL_DECK, FROST, VIOLET, rect
from game.view.bosses.world_2.w2_organic import ICE_FLESH, sinew
from game.view.enemies.enemy_shapes import SIDES, decal
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

H = ENEMY_LOOK.hull

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


def _draw_deck_edges(p: EnemyParts) -> None:
    """Armour skirts lit by violet slits, and snow drifts piled on the deck."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    top = CITADEL_DECK.top
    for s in SIDES:
        for skirt in SKIRTS:
            outline: list[OutlinePoint] = [[s * q[0], q[1]] for q in skirt]
            hull.bevel_slab(
                outline,
                [top - 0.4, top, top + 2],
                [0, 0.8],
                H.panel,
                None,
                FROST.frosted,
            )
        neon.box([0.5, 0.8, 9], VIOLET, Placement([s * 55, top + 1.2, 46], s * 0.5))
        for x, z, w in DRIFTS:
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
        sinew(flesh, [s * 30, top + 1, 32], [s * 17, top + 1, 15], 1.2, ICE_FLESH.crimson)
        rod(hull, [s * 27, top + 1, 35], [s * 14, top + 1, 18], 0.6, H.dark)


def _draw_roofs(p: EnemyParts) -> None:
    """Masts and dishes over the city, lamps along the avenue."""
    top = CITADEL_DECK.top
    avenue = CITADEL_DECK.avenue
    for s in SIDES:
        dish(p, [s * 50, top, 26], 4, [0.6, s * 0.8])
        mast(p, [s * 36, top + 19, 2], 7, AURORA if s > 0 else VIOLET)
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
    """The engine block's grilles and heat-sink fins."""
    hull = p.hull
    flesh = p.flesh
    for s in SIDES:
        grille(hull, [s * 19, -86], [10, 8], [4, 5.05])
        for dx in [4, 7, 10]:
            flesh.box(
                [1, 3, 9],
                ICE_FLESH.bone,
                Placement([s * (dx + 22), 5, -86]),
                ICE_FLESH.rime,
            )
    decal(hull, rect(8, 8, [0, -86]), 5.05, H.dark)


def draw_details(p: EnemyParts) -> None:
    """The Boreal Citadel's details (P08-R10), on its core body."""
    _draw_deck_edges(p)
    _draw_keep_detail(p)
    _draw_roofs(p)
    _draw_engine_block(p)
