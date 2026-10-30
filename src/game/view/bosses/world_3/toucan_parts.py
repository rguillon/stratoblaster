"""P09-R09, 3-2: the Toucan's parts: its huge beak cannon and its two wing pods (ducted fans).
Logical pixels, nose +Z, Y up (towards the
camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_3.toucan import TOUCAN_BEAK_TIP, TOUCAN_POD_GUNS
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_greebles import lamps
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import F, sac, sign_of, table, vein_to
from game.view.bosses.world_3.toucan_jungle import moss, segment
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import ROUND_SECTION
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The Toucan's yellow neon, and the orange one of its accents (P09-R09).
TOUCAN_YELLOW = BOSS_LOOK.neon["toucan"]
TOUCAN_ORANGE = [1, 0.36, 0.04]

# The beak's bright paint: yellow along most of it, orange towards the tip, a dark root.
BEAK_YELLOW = [0.95, 0.66, 0.1]
BEAK_ORANGE = [0.95, 0.34, 0.05]
# The beak along Z, from its root on the head to just behind the emitter (loft stations).
BEAK = table(
    [
        [20, 10, -1, 12],
        [28, 9.6, -0.6, 11.6],
        [36, 8.2, 0.4, 10.6],
        [44, 6.2, 1.8, 9.2],
        [50, 3.8, 3, 7.4],
        [53.6, 1.8, 3.9, 6.1],
    ]
)
# The bands of the beak painted orange (towards its tip) and dark (its root).
ORANGE_BANDS = [3, 4]


def beak_paint(side: int, band: int) -> Any:
    """The paint of the beak's faces: its root band dark, its last bands orange, yellow between."""
    if band == 0:
        return H.dark
    if band in ORANGE_BANDS:
        return BEAK_ORANGE
    return None


def beak(p: EnemyParts) -> None:
    """The beak cannon (P09-R09): a huge, bright, faceted beak with neon along its ridge and
    cutting edges, the laser emitter in its tip (its lens lights up as it charges)."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    # P16-R05: a living, horny beak (its bright paint the toucan's mark), a metal band at its root.
    flesh.loft(
        ROUND_SECTION,
        BEAK,
        BEAK_YELLOW,
        None,
        LoftOptions(False, beak_paint),
    )
    hull.box([20.4, 2, 2.4], H.panel, Placement([0, 4.6, 22]), H.base)
    segment(
        neon,
        [[0, 12.05, 21], [0, 7.5, 50.5]],
        [0.5, 0.4],
        TOUCAN_YELLOW,
        4,
    )
    for s in SIDES:
        segment(
            neon,
            [[s * 10.1, 1.3, 21], [s * 3.9, 3.5, 50]],
            [0.45, 0.35],
            TOUCAN_ORANGE,
            4,
        )
        # Nostrils at the root of the beak.
        hull.box([1.4, 0.6, 2.2], SHADE["soot"], Placement([s * 3.5, 11.6, 23]))
    if len(TOUCAN_BEAK_TIP) == 0:
        return
    tip = boss_point(TOUCAN_BEAK_TIP[0][0], TOUCAN_BEAK_TIP[0][1], TOUCAN_BEAK_TIP[0][2])
    hull.cylinder(
        1.9,
        2.2,
        8,
        H.dark,
        Placement(offset(tip, 0, 0, -2.8), 0, QUARTER),
        1.6,
    )
    neon.ring(2, 0.4, 8, TOUCAN_ORANGE, Placement(offset(tip, 0, 0, -2.2), 0, QUARTER))
    charge.cylinder(1.3, 0.6, 8, WHITE, Placement(offset(tip, 0, 0, -0.6), 0, QUARTER))
    muzzle(tip, "laser")


# Navigation lights: red to port (+X, the screen's left), green to starboard.
PORT_RED = [1, 0.1, 0.12]
STARBOARD_GREEN = [0.2, 1, 0.35]

# A pod's duct around its fan: an open lathe, wider at its lip (around the pod's centre).
DUCT = table([[9.6, -1.5], [11.2, -0.5], [11.4, 3.5], [10.2, 5.2]])


def wing_pod(p: EnemyParts, at: Vec3) -> None:
    """A wing pod around its centre `at` (P09-R09): a ducted fan, its lip ringed with neon, a gun
    housing under its front with the two barrels of its fans, moss on its back."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    s = sign_of(at[0])
    # P16-R05: the grafted fan duct grows out of a swollen flesh root at the wing's end.
    sac(p, offset(at, -s * 9, 1.5, -2), 5.5, F.crimson, 0.6)
    vein_to(
        p,
        [offset(at, -s * 12, 3.4, -2), offset(at, -s * 6, 4.4, 5)],
        [0, 1, 0],
        TOUCAN_ORANGE,
    )
    hull.lathe(DUCT, 10, H.panel, Placement(at, math.pi / 10), False)
    hull.cylinder(9.6, 0.5, 10, H.dark, Placement(offset(at, 0, 0.2, 0)))
    hull.cylinder(2.4, 3, 6, H.base, Placement(offset(at, 0, 0.6, 0)))
    p.rotor(offset(at, 0, 3.2, 0), 8.6)
    neon.ring(11.5, 0.8, 10, TOUCAN_YELLOW, Placement(offset(at, 0, 4, 0), math.pi / 10))
    moss(hull, offset(at, s * 8, 5.1, -7), 2.6, at[0])
    lamps(
        neon,
        [offset(at, s * 11.6, 4.4, -2)],
        1.4,
        PORT_RED if s > 0 else STARBOARD_GREEN,
    )
    hull.box([9, 3, 6], H.base, Placement(offset(at, 0, 0.3, 9)), H.panel)
    # The right pod (screen right) is on the model's -X side.
    guns = TOUCAN_POD_GUNS if s < 0 else mirror(TOUCAN_POD_GUNS)
    for m in guns:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(1.1, 5.6, 6, H.dark, Placement([x, y, z - 6.2], 0, QUARTER))
        charge.cylinder(1.15, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)
