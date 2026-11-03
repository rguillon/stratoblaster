# Copyright (c) 2026 Renaud Guillon
"""MB-STONE-IDOL-11, 3-3: the lid of the Stone Idol's crown, the moving piece of its armour (D-254).

The back of its head, from the skull cut (`SKULL`) up to the face, with the helmet, the brows, the
forehead jewel and the crown's growth on it; it flips up on a hinge across the back of the crown.
Logical pixels, nose +Z (the chin), Y up (towards the camera).
"""

from game.config.bosses.world_3.stone_idol import IDOL_JEWEL
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import WHITE
from game.view.bosses.world_3.jungle_flesh import JUNGLE_FLESH, F, gland, table
from game.view.bosses.world_3.stone_idol_parts import FACE, IDOL_NEON
from game.view.bosses.world_3.stone_idol_stone import STONE, crack, moss, vine
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from game.view.enemies.enemy_mesh import EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


# Height of the skull cut: the head is flattened there behind `CUT_Z`, and the lid lies on it,
# sunk `LID_SINK` into it.
SKULL = 7
LID_SINK = 0.3
CUT_Z = -4
# The head's section at the skull cut (its outline inset 2.5 px, as its bevel runs), behind the
# cut: the lid's plan, seen from above.
LID = table([
    [44.5, CUT_Z],
    [44.5, -11.8],
    [41.6, -29.1],
    [34.3, -40],
    [21.4, -45.6],
    [0, -47.5],
    [-21.4, -45.6],
    [-34.3, -40],
    [-41.6, -29.1],
    [-44.5, -11.8],
    [-44.5, CUT_Z],
])
# The hinge across the back of the crown (MB-STONE-IDOL-11): its pin on the head (z, height) and
# the lid's strap over it.
HINGE_Z = -50
HINGE_WIDTH = 30
# The helmet over the forehead (an Olmec headdress), outline seen from above.
HELMET = table([
    [0, -47],
    [23, -45],
    [35, -38],
    [42, -26],
    [41, -18],
    [0, -21],
    [-41, -18],
    [-42, -26],
    [-35, -38],
    [-23, -45],
])
# The neon cracks across the lid (paths seen from above), lit from inside the stone.
LID_CRACKS = table([
    [[-14, -46], [-10, -36], [-15, -28], [-12, -20]],
    [[8, -16], [14, -6]],
])


# Where the vine over the right side of the crown reaches the skull cut, at the lid's edge.
SIDE_VINE_CUT = table([43, SKULL, -24])


def draw_skull_cap(p: EnemyParts) -> None:
    """Draw the lid's flesh: the back of the head from the skull cut up to the face, its strap."""
    p.flesh.bevel_slab(
        LID, [SKULL - LID_SINK, SKULL - LID_SINK, FACE], [0, 2.5], F.sinew, None, JUNGLE_FLESH
    )
    # The hinge's strap, round its pin on the head.
    p.hull.box(
        [HINGE_WIDTH - 6, 1.6, 5], STONE.dark, Placement([0, SKULL - LID_SINK, HINGE_Z + 1.5])
    )


def draw_helmet(p: EnemyParts) -> None:
    """Draw the helmet, the neon under its front edge, and the brows over the eyes."""
    hull = p.hull
    hull.bevel_slab(HELMET, [FACE - 1, FACE + 2, FACE + 5], [0, 1.5], STONE.base, None, STONE.light)
    p.neon.box([60, 0.6, 0.6], IDOL_NEON, Placement([0, FACE + 3.2, -19.6], 0))
    # The brow ridge over the eyes, broken on the left (the model's +X).
    hull.box([30, 3.5, 6], STONE.base, Placement([-19, FACE - 0.5, -10]), STONE.light)
    hull.box([22, 3, 6], STONE.base, Placement([21, FACE - 0.5, -10], 0.08), STONE.light)
    hull.box([5, 2.4, 4], STONE.dark, Placement([36, FACE - 0.5, -12], 0.6), STONE.base)


def draw_jewel(p: EnemyParts) -> None:
    """Draw the jewel set in the forehead (MB-STONE-IDOL-04): its gilt setting and lit gem.

    The core's last-stage spiral leaves from where it is set (`stone_idol_model.draw_guns`).
    """
    for m in IDOL_JEWEL:
        jewel = boss_point(m[0], m[1], m[2])
        x = jewel[0]
        y = jewel[1]
        z = jewel[2]
        p.hull.cylinder(4.2, 1.2, 8, STONE.gilt, Placement([x, FACE + 5, z]), 3.6)
        p.neon.ring(4.3, 0.5, 8, IDOL_NEON, Placement([x, FACE + 5.6, z]))
        gem = [[3, FACE + 6.2], [3.4, y - 1.6], [0, y]]
        p.charge.lathe(gem, 6, WHITE, Placement([x, 0, z]))


def draw_crown_growth(p: EnemyParts) -> None:
    """Draw the crown's cracks, moss, vines and glands (MB-STONE-IDOL-04)."""
    hull = p.hull
    neon = p.neon
    for path in LID_CRACKS:
        crack(neon, path, FACE + 0.15, IDOL_NEON)
    crack(neon, [[-24, -40], [-30, -33], [-27, -27]], FACE + 5.1, IDOL_NEON)
    moss(hull, [-38, FACE, -6], 3.5, -38)
    moss(hull, [24, FACE + 5, -40], 4, 24)
    # The vines over the crown end at the skull cut (one on the hinge's pin): the frame lies just
    # over the lid's lowest point, and the rest hangs from the head (`stone_idol_model`).
    vine(hull, [[18, FACE + 5, -40], [30, FACE + 4.6, -34], [40, FACE, -26], SIDE_VINE_CUT])
    vine(hull, [[-10, FACE + 5, -44], [-14, FACE + 2, -49], [-15, SKULL, HINGE_Z - 0.5]])
    for s in SIDES:
        gland(p, [s * 38, FACE - 0.5, -32], 3, IDOL_NEON)


def draw_lid(p: EnemyParts) -> None:
    """Draw the lid of the crown (MB-STONE-IDOL-11): the piece that flips up as the Idol transforms.

    The back of the head over the skull cut, the helmet, the brows, the forehead jewel and the
    crown's growth on it, its strap round the hinge's pin. The third eye and the mortars lie under
    it.
    """
    draw_skull_cap(p)
    draw_helmet(p)
    draw_jewel(p)
    draw_crown_growth(p)
