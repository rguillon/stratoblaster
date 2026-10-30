"""P09-R09, 3-2: the Canopy Spider's egg sac, the part that launches its Gnat groups. Logical
pixels, nose +Z, Y up (towards the camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.final_boss_shapes import open_hatch
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.canopy_spider_legs import SPIDER_RED
from game.view.bosses.world_3.jungle_flesh import table, vein_to
from game.view.bosses.world_3.toucan_jungle import VINE, segment
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The sac's silk: a pale, dirty grey-green webbing.
SILK = [0.42, 0.45, 0.38]
# The cocoon along its axis (a lathe profile: radius, then length along -Z).
COCOON = table([[0, -9], [7, -7.5], [10.5, -3], [11, 1.5], [8.6, 6], [4.6, 8.6], [0, 9.4]])
# The eggs glowing through the silk (around the sac's centre: x, height, z).
EGGS = table(
    [
        [-4.5, 13.4, 1.5],
        [3.8, 13.8, -1],
        [0, 14.4, -5],
        [-5.4, 12.6, -7],
        [5.4, 12.6, -7.5],
    ]
)


def egg_sac(p: EnemyParts, at: Vec3) -> None:
    """The egg sac at its centre `at` (P09-R09): a cocoon of silk hanging from the abdomen's tip,
    wrapped in metal bands ringed with red neon, eggs glowing through it as the next brood
    charges, and a hatch on top that the Gnats leave from."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    centre = offset(at, 0, 4, -3)
    # P16-R06: a living egg sac of pale membrane in grafted metal bands, veined with red.
    p.flesh.lathe(COCOON, 8, SILK, Placement(centre, math.pi / 8, -QUARTER))
    for dz in [-4, 3]:
        hull.cylinder(11.2, 1.6, 8, H.base, Placement(offset(centre, 0, 0, dz), 0, QUARTER))
        neon.ring(
            11.4,
            0.6,
            8,
            SPIDER_RED,
            Placement(offset(centre, 0, 0, dz + 0.5), 0, QUARTER),
        )
    for s in SIDES:
        vein_to(
            p,
            [offset(centre, s * 9, 4, -8), offset(centre, s * 4, 9.2, 6)],
            [s * 2, 2, 0],
            SPIDER_RED,
        )
    for egg in EGGS:
        charge.cylinder(1.8, 1.2, 6, WHITE, Placement(offset(at, egg[0], egg[1], egg[2])), 1)
    open_hatch(p, offset(centre, 0, 11, 4), [6, 4])
    for s in SIDES:
        # Silk threads tying it to the abdomen.
        segment(
            hull,
            [offset(centre, s * 5, 6, 8), offset(centre, s * 3, 10, 14)],
            [0.4, 0.4],
            VINE,
            4,
        )
