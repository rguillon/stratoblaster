"""P08-R10, 2-1: the Narwhal's destroyable parts (its horn lance, torpedo tubes and ballast pods),
ported from `bosses/world-2/narwhal-parts.ts`. Logical pixels, nose +Z, Y up; each drawn around
its centre `at`."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.record import record  # noqa: E402
from game.view.bosses.final_boss_shapes import barrels, shift  # noqa: E402
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    sinew,
)
from game.view.enemies.enemy_shapes import POD_SECTION, side_stripe  # noqa: E402
from render.geometry.organic import organ  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

H = ENEMY_LOOK.hull
WHITE = [1.0, 1.0, 1.0]
QUARTER = math.pi / 2
# Light metal: the horn's ridges and the tubes' rims.
EDGE = [0.24, 0.24, 0.27]
# The horn's darker bone bands.
BONE_DARK = [0.12, 0.11, 0.1]
# The side of a pod's section that faces the nose or the tail, painted with the rime.
POD_BACK = 2

# A submarine's round hull section (`SolidBuilder.loft`), counter-clockwise seen from the nose:
# a rounded belly, full sides, shoulders and a flat back (side 4) where snow settles.
SUB_SECTION = [
    [0.4, 0.0],
    [0.92, 0.2],
    [1.0, 0.5],
    [0.85, 0.8],
    [0.35, 1.0],
    [-0.35, 1.0],
    [-0.85, 0.8],
    [-1.0, 0.5],
    [-0.92, 0.2],
    [-0.4, 0.0],
]

# The horn: segments from its root to its tip, each turned a little more (a spiral).
HORN = record(
    {
        "root": 52,
        "tip": 90,
        "height": 4.5,
        "radius": 4.2,
        "segments": 7,
        "twist": 0.55,
    }
)


def _sign(x: float) -> float:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def horn_lance(p: EnemyParts, at: Vec3, n: Rgb) -> None:
    """The horn lance (P08-R10): a collar on the nose and a long spiral horn, a teal light
    winding round it, its tip glowing as its laser charges."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    # P16-R06: a spiral horn of bone, a metal collar grafted where it leaves the head.
    root = HORN.root
    tip = HORN.tip
    height = HORN.height
    radius = HORN.radius
    segments = HORN.segments
    twist = HORN.twist
    hull.cylinder(5.4, 5, 8, H.panel, Placement([at[0], height, root - 4], 0, QUARTER), 4.4)
    neon.ring(5.5, 0.8, 8, n, Placement([at[0], height, root - 2], 0, QUARTER))
    step = (tip - root - 3) / segments
    for i in range(segments):
        r0 = radius * (1 - i / segments)
        r1 = radius * (1 - (i + 1) / segments) + 0.3
        place = Placement([at[0], height, root + i * step], 0, QUARTER, i * twist)
        flesh.cylinder(r0, step, 5, ICE_FLESH.bone if i % 2 == 0 else BONE_DARK, place, r1)
        # The light winding round the horn, a bead on each segment.
        a = i * 1.3
        r = r0 * 0.9
        neon.box(
            [0.9, 0.9, step * 0.7],
            n,
            Placement(
                [
                    at[0] + math.sin(a) * r,
                    height + math.cos(a) * r - 0.45,
                    root + (i + 0.3) * step,
                ]
            ),
        )
    end = root + segments * step
    charge.cylinder(0.6, tip - end, 5, WHITE, Placement([at[0], height, end], 0, QUARTER), 0)
    muzzle([at[0], height, tip], "laser")


# A torpedo tube's blister (loft stations around its centre: z, half width, bottom, top).
BLISTER = [
    [-14.0, 3.5, 1.0, 8.0],
    [-6.0, 6.0, 0.0, 10.0],
    [8.0, 6.0, 0.0, 10.0],
    [11.0, 5.0, 0.5, 9.5],
]


def torpedo_tube(p: EnemyParts, at: Vec3, n: Rgb) -> None:
    """A torpedo tube (P08-R10): a blister on the hull's flank, two tube mouths at its front
    (their torpedoes glowing as a salvo charges), a teal line along its outer side."""
    s = _sign(at[0])
    # P16-R06: a swollen blister of flesh on the flank, metal tube mouths grafted at its front.
    p.flesh.loft(
        POD_SECTION,
        BLISTER,
        ICE_FLESH.purple,
        Placement(at),
        LoftOptions(
            False,
            lambda side, band: ICE_FLESH.rime if side == POD_BACK else None,
        ),
    )
    organ(p.vein, 1, 5, n, Placement(shift(at, [s * 4, 8, -6])), 0.6)
    outer = 0 if s > 0 else 4
    p.neon.loft(
        side_stripe(POD_SECTION, outer, [0.3, 0.8], 1.06),
        BLISTER[0:3],
        n,
        Placement(at),
        LoftOptions(True),
    )
    p.hull.box([11, 7, 0.6], EDGE, Placement(shift(at, [0, 1.5, 11])))
    barrels(p, shift(at, [0, 5, 11]), [2, 5], [1.8, 1.5], "missile")
    crystals(p.flesh, shift(at, [s * 3, 9, -10]), 2.6, 2)


# A ballast pod (loft stations around its centre: z, half width, bottom, top).
POD = [
    [-21.0, 3.0, 2.0, 8.0],
    [-14.0, 8.0, -2.0, 12.0],
    [10.0, 8.0, -2.0, 12.0],
    [18.0, 4.5, 1.0, 9.0],
]


def ballast_pod(p: EnemyParts, at: Vec3, n: Rgb) -> None:
    """A ballast pod (P08-R10): a long tank on its pylon, frost on its back, a teal ring round
    its middle, two fan guns at its front and a flood vent on top."""
    s = _sign(at[0])
    # P16-R06: a ballast sac of flesh, held in metal bands, a gland on its back.
    p.flesh.loft(
        POD_SECTION,
        POD,
        ICE_FLESH.membrane,
        Placement(at),
        LoftOptions(
            False,
            lambda side, band: ICE_FLESH.rime if side == POD_BACK and band != 1 else None,
        ),
    )
    for z in [-6, 2]:
        p.neon.ring(8.4, 0.8, 6, n, Placement(shift(at, [0, 5, z]), 0, QUARTER, math.pi / 6))
    p.hull.ring(
        8.6,
        2,
        6,
        H.panel,
        Placement(shift(at, [0, 5, -13]), 0, QUARTER, math.pi / 6),
    )
    organ(p.vein, 1.4, 5, n, Placement(shift(at, [0, 11.4, -16])), 0.6)
    barrels(p, shift(at, [0, 6, 18]), [2, 5], [1.2, 4])
    crystals(p.flesh, shift(at, [-s * 3, 11.6, 6]), 2.6)
    sinew(p.flesh, shift(at, [-s * 6, 6, -12]), shift(at, [-s * 14, 7, -14]), 1.4)
