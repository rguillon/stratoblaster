# Copyright (c) 2026 Renaud Guillon
"""MB-JAGUAR-03, MB-JAGUAR-11, 3-5: the Jaguar's wing pelt (the armour it sheds, D-254), its fins.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera; +X is the
screen's left.
"""

import math

from game.config.bosses.world_3.jaguar import JAGUAR_WING
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.mini_boss_greebles import vent
from game.view.bosses.world_3.jaguar_parts import AMBER, COAT, rosette
from game.view.bosses.world_3.jungle_flesh import table, vein_to
from game.view.enemies.enemy_shapes import SIDES, flip_x
from render.geometry.outline import inset_outline
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull

# Heights of the wing: belly, edge, top.
WING_Y = [-3, 0, 3]
# The pelt over a wing (MB-JAGUAR-11): the wing's spotted skin, a plate from just under the wing's
# top up to `PELT_Y[2]`, over the wing's top face (the design's outline inset as the wing's bevel
# is). The +X one (the screen's left wing); the other is its mirror image.
PELT_Y = [WING_Y[2] - 0.3, WING_Y[2], 4.5]
PELT = table([[point[0], -point[1]] for point in JAGUAR_WING])
# The rosettes on the pelt (right half, mirrored): where and how big.
SPOTS = table([
    [24, 4, 3.2],
    [35, -9, 3],
    [48, -18, 2.3],
    [26, -20, 3.2],
    [19, -33, 2.5],
    [39, -27, 2],
    [16, 18, 2.4],
])
# The canted fins near the tail, like a stealth fighter's: where they stand on the wing (x, z),
# how tall they are and how far they lean outwards (radians); their lights run along their tops.
FIN = table([13, -34, 8, 0.5])


def pelt_top(outline: list[Any]) -> list[Any]:
    """Return a pelt's `outline` (XZ) inset to the wing's top face: 2 px, as the wing's bevel."""
    n = len(outline)
    area = 0.0
    for i in range(n):
        a = outline[i]
        b = outline[(i + 1) % n]
        area += a[0] * b[1] - b[0] * a[1]
    ring = list(outline) if area > 0 else [outline[n - 1 - k] for k in range(n)]
    return inset_outline(ring, WING_Y[2] - WING_Y[1] - 1)


def draw_pelt(p: EnemyParts) -> None:
    """Draw the wings' pelt (MB-JAGUAR-11): the armour it sheds at its transformation.

    On each wing, a plate of spotted ochre armour over the wing's top face, its rosettes
    (MB-JAGUAR-03), a vent and the veins on it. The lances lie folded under it.
    """
    for s in SIDES:
        outline = PELT if s > 0 else flip_x(PELT)
        p.hull.bevel_slab(pelt_top(outline), PELT_Y, [0, 1], COAT)
        # The rosettes are painted on the pelt's living skin (its plates stay ochre as they fly).
        for spot in SPOTS:
            rosette(p.flesh, [s * spot[0], spot[1]], spot[2], PELT_Y[2] + 0.05)
        vent(p.hull, [s * 14, PELT_Y[2] - 0.1, -22], [4, 9], 3, s * 0.2)
        vein_to(
            p,
            [[s * 14, PELT_Y[2] - 0.2, 4], [s * 36, PELT_Y[2] - 0.2, -30]],
            [0, 0, 6],
            AMBER,
        )


def draw_fins(p: EnemyParts) -> None:
    """Draw the canted fins near the tail, standing on the wing, their lights along their tops."""
    x = FIN[0]
    z = FIN[1]
    height = FIN[2]
    lean = FIN[3]
    top_x = x + height * math.sin(lean)
    top_y = WING_Y[2] + height * math.cos(lean)
    for s in SIDES:
        foot = Placement([s * x, WING_Y[2], z], 0, 0, -s * lean)
        p.hull.box([1, height, 12], H.panel, foot, COAT)
        top = Placement([s * top_x, top_y - 0.2, z], 0, 0, -s * lean)
        p.neon.box([0.5, 0.5, 10], AMBER, top)
