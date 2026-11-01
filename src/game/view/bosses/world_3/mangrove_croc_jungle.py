# Copyright (c) 2026 Renaud Guillon
"""MB-MANGROVE-CROC-05, FB-RIVER-LEVIATHAN-06, 3-1: the river growth.

It grows on the Mangrove Croc and the River Leviathan (BOSS-50, the World 3 theme: dark metal with
neon, plus moss, vines and stone). Logical pixels, nose +Z, Y up.
"""

import math

from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from render.geometry.outline import OutlinePoint
from render.geometry.solids import SolidBuilder

type Rgb = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# Swamp shades: moss, vines, river stone, old bone-white teeth. D-231: clear greens and a grey mud,
# not olive and brown (no khaki with the enemies' yellow and green).
SWAMP = record({
    "moss": [0.035, 0.15, 0.045],
    "mossLight": [0.05, 0.2, 0.06],
    "vine": [0.02, 0.1, 0.03],
    "stone": [0.17, 0.16, 0.14],
    "tooth": [0.42, 0.4, 0.34],
    "mud": [0.08, 0.08, 0.075],
})


def moss(hull: SolidBuilder, outline: list[OutlinePoint], y: float) -> None:
    """Add a patch of moss lying on a hull at height `y`: a thin, lumpy slab over `outline`."""
    hull.slab(outline, [y - 0.3, y + 0.6], SWAMP.moss, None, SWAMP.mossLight)


def vine(hull: SolidBuilder, start: Vec3, end: Vec3, sag: float) -> None:
    """Add a vine hanging from `start` to `end`, sagging `sag` below the line between them.

    Two thin stems meeting at the low point, a leaf there.
    """
    low: Vec3 = [
        (start[0] + end[0]) / 2,
        (start[1] + end[1]) / 2 - sag,
        (start[2] + end[2]) / 2,
    ]
    for pair in [[start, low], [low, end]]:
        a = pair[0]
        b = pair[1]
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        dz = b[2] - a[2]
        length = math.hypot(dx, dy, dz)
        place = Placement(a, math.atan2(dx, dz), math.acos(dy / length))
        hull.cylinder(0.45, length, 3, SWAMP.vine, place)
    hull.box([2.2, 0.3, 1.4], SWAMP.mossLight, Placement(low, start[0] - end[0]))


def scutes(hull: SolidBuilder, points: list[Vec3], size: float) -> None:
    """Armour scutes along a ridge: a short row of low pyramids, `size` wide, at `points`."""
    for at in points:
        hull.cylinder(size, size * 0.8, 4, H.panel, Placement(at, QUARTER / 2), 0)


def stone(hull: SolidBuilder, at: Vec3, size: float, turn: float = 0) -> None:
    """Add a mossy river stone set into a hull: a squat, faceted lump."""
    hull.cylinder(size, size * 0.55, 5, SWAMP.stone, Placement(at, turn), size * 0.6)
    hull.cylinder(
        size * 0.6,
        size * 0.15,
        5,
        SWAMP.moss,
        Placement([at[0], at[1] + size * 0.55, at[2]], turn),
    )


def barrel_to(
    parts: Any,
    tip: list[float],
    dims: list[float],
    kind: str = "gun",
) -> None:
    """Add a barrel along +Z ending at the muzzle `tip` (playfield, `boss_point`).

    `dims` is `[radius, length]`. Its dark tube, a charge light at its mouth, and the muzzle's mark
    (of `kind`).
    """
    x, y, z = boss_point(tip[0], tip[1], tip[2])
    radius = dims[0]
    length = dims[1]
    light = radius * 1.2
    parts.hull.cylinder(
        radius,
        length,
        6,
        H.dark,
        Placement([x, y, z - light - length], 0, QUARTER),
    )
    parts.charge.cylinder(
        radius * 0.92,
        light,
        6,
        WHITE,
        Placement([x, y, z - light], 0, QUARTER),
    )
    parts.muzzle([x, y, z], kind)
