"""P09-R09, 3-4: the Mosquito's parts (its buzzing wings and its proboscis) and its swamp growth.
Logical pixels, nose +Z, Y up (towards the
camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_3.mosquito import MOSQUITO_NEEDLE, MOSQUITO_WING_GUNS
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_shapes import sided
from game.view.bosses.mini_boss_greebles import seam
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import F, sign_of, table
from game.view.enemies.enemy_shapes import POD_SECTION
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The Mosquito's pink neon.
MOSQUITO_PINK = BOSS_LOOK.neon["mosquito"]
# Swamp moss on its back and the dark, oily sheen of its wing membranes (World 3 growth).
MOSS = [0.13, 0.2, 0.07]
MEMBRANE = [0.11, 0.08, 0.13]


def moss(hull: SolidBuilder, points: list[Vec3], size: float = 2.4) -> None:
    """Moss tufts at each point (`[x, y, z]`): low, lumpy cushions of growth."""
    for i in range(len(points)):
        r = size * (0.8 + (i % 3) * 0.2)
        hull.cylinder(r, r * 0.5, 5, MOSS, Placement(points[i], i * 0.7), r * 0.45)


# The left wing seen from above (model +X), from its root's leading edge out and back.
WING = table(
    [
        [10, 1],
        [22, 3],
        [36, 2],
        [47, -1],
        [52, -5],
        [51, -9],
        [44, -12],
        [30, -13],
        [18, -11],
        [10, -7],
    ]
)
# The membrane's neon veins, root to tip (left wing).
VEINS = table(
    [
        [[12, 0], [49, -4]],
        [[12, -4], [44, -10]],
        [[14, -7], [30, -12]],
    ]
)
# Height of the membrane: a thin film over the pod.
WING_Y = 3
# A wing pod's nacelle under the membrane (loft stations around the pod's centre).
NACELLE = table(
    [
        [-7, 2.5, -2, 2],
        [-2, 4, -2.5, 3],
        [5, 3.6, -2, 2.6],
        [8, 2.2, -1, 1.6],
    ]
)


def wing(p: EnemyParts, at: Vec3) -> None:
    """A wing around its pod's centre `at` (P09-R09), drawn on its buzzing joint: a long, thin
    membrane veined with pink neon, and under it the fan pod with its two barrels."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    s = sign_of(at[0])
    # P16-R05: a living membrane wing on a bone spar, its fan pod a grafted metal nacelle in a
    # flesh sheath.
    flesh.bevel_slab(
        sided(WING, s),
        [WING_Y - 0.3, WING_Y, WING_Y + 0.5],
        [0.3, 0.3],
        MEMBRANE,
    )
    for vein in VEINS:
        a = vein[0]
        b = vein[1]
        seam(
            neon,
            [s * a[0], a[1]],
            [s * b[0], b[1]],
            [WING_Y + 0.6, 0.5, 0.25],
            MOSQUITO_PINK,
        )
    seam(flesh, [s * 10, 1], [s * 47, -1], [WING_Y + 0.4, 1.2, 0.8], F.bone)
    neon.box([1.4, 0.8, 1.4], MOSQUITO_PINK, Placement([s * 51, WING_Y + 0.6, -7]))
    flesh.loft(POD_SECTION, NACELLE, F.purple, Placement([at[0], -1, at[2]]))
    hull.cylinder(3, 2, 6, H.panel, Placement([at[0], 0, at[2] + 2], 0, QUARTER))
    # The left wing (screen left) is on the model's +X side.
    guns = MOSQUITO_WING_GUNS if s > 0 else mirror(MOSQUITO_WING_GUNS)
    for m in guns:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(0.9, 6, 6, H.dark, Placement([x, y, z - 6.6], 0, QUARTER))
        charge.cylinder(0.95, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)


# The proboscis's socket under the head (a lathe profile): the needle turns in it.
SOCKET = table([[5.5, 0], [6, 2], [4.5, 4.5], [0, 5]])


def proboscis(p: EnemyParts, at: Vec3) -> None:
    """The proboscis around its centre `at` (P09-R09): a ringed socket the needle turns in."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a fleshy mouthpart sheath, metal blades grafted either side of it.
    flesh.lathe(SOCKET, 8, F.crimson, Placement(offset(at, 0, -1, 0), math.pi / 8))
    neon.ring(6.1, 0.6, 8, MOSQUITO_PINK, Placement(offset(at, 0, 1, 0), math.pi / 8))
    for s in [-1, 1]:
        hull.box(
            [1.2, 1.6, 7],
            SHADE["edge"],
            Placement(offset(at, s * 6, 1, -2), s * 0.3),
        )


# The needle (a lathe profile along its axis, from its root to its point).
NEEDLE = table([[2.6, 0], [2.2, 3], [1.2, 6], [0.9, 14], [0.4, 19]])


def needle(p: EnemyParts, at: Vec3) -> None:
    """The proboscis's needle, turning on its socket (P09-R09, D-073: it aims its laser at the
    player during the warning line): a long, thin spike ringed in pink, its point glowing as the
    laser charges."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(MOSQUITO_NEEDLE) == 0:
        return
    tip = boss_point(MOSQUITO_NEEDLE[0][0], MOSQUITO_NEEDLE[0][1], MOSQUITO_NEEDLE[0][2])
    x = tip[0]
    y = tip[1]
    z = tip[2]
    root: Vec3 = [x, y, at[2] + 1]
    hull.lathe(NEEDLE, 6, H.dark, Placement(root, 0, QUARTER))
    for along in [3.5, 8, 12]:
        neon.ring(
            1.6 - along * 0.05,
            0.5,
            6,
            MOSQUITO_PINK,
            Placement(offset(root, 0, 0, along), 0, QUARTER),
        )
    hull.cylinder(3.2, 2.6, 8, H.panel, Placement(offset(root, 0, 0, -1.5), 0, QUARTER))
    charge.cylinder(0.9, 1.6, 6, WHITE, Placement([x, y, z - 1.6], 0, QUARTER), 0.2)
    muzzle(tip, "laser")
