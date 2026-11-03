# Copyright (c) 2026 Renaud Guillon
"""FB-OBSIDIAN-GOLEM-16, FB-OBSIDIAN-GOLEM-18, 4-3: the Obsidian Golem's armour (D-254).

Drawn as pieces of their own, lying on the core as the boss rests (BOSS-42): the two flank slabs
(`flanks-left` at +X, `flanks-right` at -X), obsidian plates on the torso's flanks carrying the
pauldrons, that lift like gull-wing doors at its first transformation; and the spine plating
(`spine`), an obsidian ridge along the hump's crest with the helm at its end, that bursts off at its
second, leaving a dark metal spine the model draws itself. Logical pixels, nose +Z, Y up; a config
outline (x, y) is drawn at (-x, -y).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_armour import plate_pieces
from game.view.bosses.mini_boss_greebles import vent
from game.view.bosses.mini_boss_shapes import SHADE, WHITE, H, offset
from game.view.bosses.world_4.living_forge import glands, magma_vein
from game.view.bosses.world_4.obsidian_golem_parts import (
    GOLEM_NEON,
    MAGMA,
    OBSIDIAN,
    crack,
)
from game.view.enemies.enemy_shapes import HULL_SECTION, flip_x
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The torso's top, where the flank slabs lie.
TORSO_TOP = 16
# A flank slab (the +X one; the other is its mirror): on the torso's top face, from the hump's foot
# at x 14 to the face's edge. Its config outline is this one, Z reversed.
SLAB: list[OutlinePoint] = [
    [14, 24],
    [17, 24],
    [29, 16],
    [36, 4],
    [34.5, -15],
    [26, -29],
    [14, -31],
]
SLAB_TOP = TORSO_TOP + 1.5
# The pauldron's centre over the shoulder (x, z) and its dome (a lathe profile from the slab's foot
# up): its outer edge is the slab's hinge (`moving_region("flanks", ...)`: x 51, 16 high).
PAULDRON_AT = [38.0, 2.0]
PAULDRON = [
    [13.0, 0.0],
    [13.6, 4.0],
    [10.0, 9.0],
    [4.0, 11.0],
    [0.0, 11.4],
]
# The spine ridge along the hump's crest (loft stations, back to front: z, half width, bottom,
# top), sunk a px into the hump and standing 1.6 px proud of it.
RIDGE = [
    [-16.0, 10.0, 26.0, 28.6],
    [-8.0, 12.0, 26.6, 29.4],
    [0.0, 12.0, 25.8, 28.6],
    [8.0, 10.0, 25.0, 27.6],
]
# The magma seams across the ridge, as paths of points (x, z), and their height.
SEAMS = [
    [
        [-11.0, 2.0],
        [-4.0, -4.0],
        [3.0, -1.0],
        [11.0, -7.0],
    ],
    [
        [-11.0, -10.0],
        [-4.0, -7.0],
        [2.0, -14.0],
        [10.0, -11.0],
    ],
]
SEAM_Y = 28.9
# The helm: a small helm low on its chest at the ridge's end, from its nape to its brow.
HELM = [
    [8.0, 9.0, 16.0, 28.0],
    [16.0, 10.0, 16.0, 29.0],
    [22.0, 8.0, 17.0, 26.0],
]
# How much lower than the ridge the dark spine it leaves is drawn.
SPINE_DROP = 1.2


def draw_flank(s: float) -> Any:
    """Return the drawing of the flank slab at side `s` (FB-OBSIDIAN-GOLEM-16).

    An obsidian plate on the torso's flank; on it the pauldron (a dome ringed in orange, cracked
    with magma), the flank's magma vein and gland, a vent and a soot patch. The shoulder cannon's
    mount stands beside it while the cannon lives; the heavy cannon lies folded under it.
    """

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        slab = SLAB if s > 0 else flip_x(SLAB)
        hull.bevel_slab(
            slab, [TORSO_TOP, TORSO_TOP + 0.5, SLAB_TOP], [0, 0.6], H.dark, None, OBSIDIAN
        )
        at: Vec3 = [s * PAULDRON_AT[0], TORSO_TOP, PAULDRON_AT[1]]
        hull.lathe(PAULDRON, 8, OBSIDIAN, Placement(at, math.pi / 8))
        neon.ring(13.7, 0.8, 8, GOLEM_NEON, Placement(offset(at, 0, 1.4, 0), math.pi / 8))
        crack(neon, [[s * 32, 6], [s * 38, 0], [s * 44, 3]], at[1] + 9.8)
        magma_vein(
            p,
            [
                [s * 27, SLAB_TOP + 0.2, 14],
                [s * 33, SLAB_TOP + 0.2, -2],
                [s * 26, SLAB_TOP + 0.2, -24],
            ],
            1.4,
        )
        glands(p, [[s * 24.5, SLAB_TOP, -28.5]], 2.4, GOLEM_NEON)
        vent(hull, [s * 18, SLAB_TOP + 0.2, -22], [8, 6], 3, s * 0.2)
        hull.box([10, 0.5, 8], SHADE["soot"], Placement([s * 26, SLAB_TOP + 0.1, 8 + s * 4]))

    return draw


def _draw_helm(p: Any) -> None:
    """Draw the helm: a small helm with a glowing visor and a crest, low on the chest."""
    p.hull.loft(HULL_SECTION, HELM, H.panel)
    p.neon.box([14, 1.2, 1], GOLEM_NEON, Placement([0, 25.6, 22.2]))
    p.charge.box([10, 0.6, 0.6], WHITE, Placement([0, 26, 22.5]))
    p.hull.box([3, 4, 10], SHADE["edge"], Placement([0, 28.6, 14]))


def draw_spine(p: Any) -> None:
    """Draw the spine plating (FB-OBSIDIAN-GOLEM-18): the obsidian ridge along the hump's crest.

    Magma seams across it, the helm at its end over the chest (its brow guns are the core's and
    stay). The sweeper and the mortars lie folded under it.
    """
    p.hull.loft(HULL_SECTION, RIDGE, OBSIDIAN)
    for path in SEAMS:
        crack(p.neon, path, SEAM_Y)
    _draw_helm(p)


def draw_spine_frame(p: Any) -> None:
    """Draw the dark metal spine the ridge leaves (BOSS-44): a lower ridge of dark metal.

    Three ribs across it and a thin magma seam along its crest; the sweeper's pod stands where
    the helm was.
    """
    look = BOSS_LOOK.frame
    stations = [[st[0], st[1], st[2], st[3] - SPINE_DROP] for st in RIDGE]
    p.hull.loft(HULL_SECTION, stations, look.floor)
    for z in [-13, -4, 5]:
        p.hull.box(
            [22, look.ribHeight * 0.4, look.ribWidth],
            look.metal,
            Placement([0, 27.4 - abs(z + 4) * 0.08, z]),
        )
    p.neon.box([0.6, 0.4, 22], MAGMA, Placement([0, 27.8, -4]))


def slab_pieces(s: float) -> list[Any]:
    """Return the pieces the flank slab at side `s` bursts into: obsidian plates cracked from it.

    At the slab's own height (not the pauldron's, where the default plates would lie); its share
    of the boss's piece budget, three regions sharing it.
    """
    most = math.floor(BOSS_LOOK.armour.bossChunks / 3)
    slab = SLAB if s > 0 else flip_x(SLAB)
    return [piece[0] for piece in plate_pieces([slab], [TORSO_TOP, SLAB_TOP], OBSIDIAN, most)]


# The regions' drawings (`drawing.armour`): the flank slabs (`flanks-right` at -X: config x > 0)
# and the spine ridge with the frame it leaves.
OBSIDIAN_GOLEM_ARMOUR = {
    "flanks-right": {"whole": draw_flank(-1), "pieces": slab_pieces(-1)},
    "flanks-left": {"whole": draw_flank(1), "pieces": slab_pieces(1)},
    "spine": {"whole": draw_spine, "frame": draw_spine_frame},
}
