# Copyright (c) 2026 Renaud Guillon
"""FB-SKY-TEMPLE-02, 3-3: the living beast the Sky Temple grew on.

A huge, swollen body of moss-skinned flesh carrying the stone tiers on its back like a shell, roots
of sinew hanging from it, veins climbing the stones to the sanctum. Its back is flat under the tiers
(the stone of the wedges and the terrace, its armour, is sunk into it; D-254). Logical pixels, nose
+Z, Y up.
"""

from game.view.bosses.world_3.jungle_flesh import JUNGLE_FLESH, F, gland, sinew, table, vein_to
from game.view.bosses.world_3.sky_temple_parts import SUMMIT, TEMPLE_CYAN, TIERS
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from game.view.enemies.enemy_mesh import EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


# The beast's section (counter-clockwise seen from the nose): a round belly and flanks under a
# broad flat back, the shell the tiers stand on.
BEAST_SECTION = table([
    [0.4, 0],
    [0.9, 0.2],
    [1, 0.5],
    [0.95, 0.85],
    [0.75, 1],
    [-0.75, 1],
    [-0.95, 0.85],
    [-1, 0.5],
    [-0.9, 0.2],
    [-0.4, 0],
])
# The height of its flat back: the first stone tier stands on it, the armour's stone sunk 0.3 in.
BACK = TIERS.height - 0.4
# Where the glands sit on its shoulders, at the corners (model px from the centre, and height).
GLAND_OUT = TIERS.halves[0] * 0.8
GLAND_Y = 5.2


def body_stations() -> list[list[float]]:
    """Return the body under the lowest tier, tail to front.

    Its loft stations: z, half width, bottom, top. Its back is flat at `BACK` under the tiers,
    sloping a little to its ends, which reach out under the corner obelisks.
    """
    half = TIERS.halves[0]
    return [
        [-half - 2, half * 0.75, 2, BACK - 1],
        [-half * 0.7, half * 0.98, -3, BACK],
        [0, half * 1.04, -4, BACK],
        [half * 0.7, half * 0.98, -3, BACK],
        [half + 2, half * 0.75, 2, BACK - 1],
    ]


def temple_body(p: EnemyParts) -> None:
    """Add the body of the beast (FB-SKY-TEMPLE-02), in place of the lowest stone tier."""
    p.flesh.loft(BEAST_SECTION, body_stations(), JUNGLE_FLESH)
    half = TIERS.halves[0]
    for s in SIDES:
        for z in [-40, 0, 40]:
            sinew(
                p,
                [[s * half * 0.9, 0, z], [s * (half + 3), -12, z + 6]],
                [s * 2, -2, 0],
                2.4,
            )
    # Veins climbing the tiers along their diagonals up to the sanctum, from the glands on the
    # beast's shoulders at its corners (beside the wedges, which slide out past them).
    for x in SIDES:
        for z in SIDES:
            start: Vec3 = [x * GLAND_OUT, GLAND_Y + 0.8, z * GLAND_OUT]
            end: Vec3 = [x * 12, SUMMIT + 0.4, z * 12 - 8]
            vein_to(p, [start, end], [0, 6, 0], TEMPLE_CYAN, 1.6)
            gland(p, [x * GLAND_OUT, GLAND_Y, z * GLAND_OUT], 3, TEMPLE_CYAN)


def temple_reactors(p: EnemyParts, z: float, nozzles: list[float]) -> None:
    """Its reactors (GFX-ART-13, FB-SKY-TEMPLE-02): each in a flesh sac at the back of the beast."""
    for x in nozzles:
        reactor_sac(p, table([x, 0, z]), 4.5, table(TEMPLE_CYAN), F.sinew, None)
