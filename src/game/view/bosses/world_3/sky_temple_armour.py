# Copyright (c) 2026 Renaud Guillon
"""FB-SKY-TEMPLE-13, FB-SKY-TEMPLE-14, 3-3: the Sky Temple's armour (D-254).

Its four corner wedges, pieces of the stone tiers that slide out as it transforms (BOSS-45), and its
back terrace, the tiers' steps behind the sanctum, which bursts off (BOSS-42): each drawn as a piece
of its own, in place as it rests, the core's tiers notched where they lie (`tier_outline`). Logical
pixels, nose +Z (its grand stair, down the screen), Y up (towards the camera).
"""

from game.view.bosses.mini_boss_shapes import WHITE, neon_band
from game.view.bosses.world_3.sky_temple_parts import SUMMIT, TEMPLE_GOLD, TIERS
from game.view.bosses.world_3.stone_idol_stone import STONE, leaf, moss
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


# A corner wedge's column: from `WEDGE_IN` out across the boss and from `WEDGE_FROM` back along it
# (|x| and |z|, model px). The corners of the first two stone tiers lying in it make the wedge.
WEDGE_IN = 34
WEDGE_FROM = 20
# The back terrace: the tiers' steps behind the sanctum's back wall, between the back wedges.
TERRACE_FRONT = -20
# The armour's stone is sunk this much into the beast's flat back (its frame floor shows 0.6 px
# over the back once it is gone).
SINK = 0.3
# The gold trim under a tier's rim: its depths under the tier's top, and its scale out of the tier.
TRIM = [1.4, 0.6]
TRIM_SCALE = [1.006, 1.006]
# Where the braziers stand on the summit (|x| and |z|).
BRAZIER_OUT = TIERS.halves[len(TIERS.halves) - 1] - 4


def tier_outline(half: float) -> list[list[float]]:
    """Return the core's outline (XZ) of a stone tier of half width `half`: its square, notched.

    Its four corners (the wedges, from `WEDGE_IN` out and `WEDGE_FROM` back) and its back behind
    `TERRACE_FRONT` (the terrace) are armour, drawn apart.
    """
    w = WEDGE_IN
    f = WEDGE_FROM
    if half <= w:
        return [[-half, TERRACE_FRONT], [half, TERRACE_FRONT], [half, half], [-half, half]]
    return [
        [-half, TERRACE_FRONT],
        [half, TERRACE_FRONT],
        [half, f],
        [w, f],
        [w, half],
        [-w, half],
        [-w, f],
        [-half, f],
    ]


def tier_trim(p: EnemyParts, outline: list[Any], tier: int, color: Any) -> None:
    """Add the neon trim under the rim of `tier`, along `outline` (XZ)."""
    top = (tier + 1) * TIERS.height
    neon_band(p.neon, outline, [top - TRIM[0], top - TRIM[1]], TRIM_SCALE, color)


def stone_block(p: EnemyParts, tier: int, xs: list[float], zs: list[float]) -> None:
    """Add a block of `tier`'s stone over the X span `xs` and the Z span `zs`.

    The first tier's is sunk `SINK` into the beast's back.
    """
    low = tier * TIERS.height - (SINK if tier == 1 else 0)
    top = (tier + 1) * TIERS.height
    p.hull.box(
        [abs(xs[1] - xs[0]), top - low, abs(zs[1] - zs[0])],
        STONE.base,
        Placement([(xs[0] + xs[1]) / 2, low, (zs[0] + zs[1]) / 2]),
        STONE.light,
    )


def brazier(p: EnemyParts, spot: Vec3) -> None:
    """Add a brazier at `spot` on the summit: a stone bowl, flaring as the next attack charges."""
    p.hull.cylinder(2.6, 2.4, 6, STONE.dark, Placement(spot), 3)
    p.charge.cylinder(2, 3, 6, WHITE, Placement([spot[0], spot[1] + 2.4, spot[2]]), 0.3)


def corner_wedge(sx: float, sz: float, moss_at: Any) -> Any:
    """Return the drawing of the corner wedge at the signs `sx`, `sz` of X and Z (BOSS-45).

    The corners of the first two stone tiers lying in its column, their gold trims, and a patch of
    moss at `moss_at` (`[x, y, z, size]`; None for none) on the lower corner's top.
    """

    def draw(p: EnemyParts) -> None:
        for tier in [1, 2]:
            half = TIERS.halves[tier]
            stone_block(p, tier, [sx * WEDGE_IN, sx * half], [sz * WEDGE_FROM, sz * half])
            corner = [
                [sx * WEDGE_IN, sz * WEDGE_FROM],
                [sx * half, sz * WEDGE_FROM],
                [sx * half, sz * half],
                [sx * WEDGE_IN, sz * half],
            ]
            tier_trim(p, corner, tier, TEMPLE_GOLD)
        if moss_at != None:
            moss(p.hull, [moss_at[0], moss_at[1], moss_at[2]], moss_at[3], moss_at[0])

    return draw


def back_terrace(p: EnemyParts) -> None:
    """Draw the back terrace (FB-SKY-TEMPLE-13): the armour that bursts off for the mortar.

    The steps of the three stone tiers behind the sanctum, between the back wedges, their gold
    trims, the back braziers on the top step, moss and a leaf fallen there.
    """
    for tier in [1, 2, 3]:
        half = TIERS.halves[tier]
        stone_block(p, tier, [-WEDGE_IN, WEDGE_IN], [-half, TERRACE_FRONT])
        step = [
            [-WEDGE_IN, TERRACE_FRONT],
            [WEDGE_IN, TERRACE_FRONT],
            [WEDGE_IN, -half],
            [-WEDGE_IN, -half],
        ]
        tier_trim(p, step, tier, TEMPLE_GOLD)
    for s in [-1, 1]:
        brazier(p, [s * BRAZIER_OUT, SUMMIT, -BRAZIER_OUT])
    moss(p.hull, [20, SUMMIT, -30], 3, 20)
    leaf(p.hull, [10, SUMMIT, -30], 3, 1)
