"""P08-R10, 2-4: the Glacier Colossus's parts
Logical pixels, nose +Z, Y up (towards the camera); each part is drawn around its centre `at`
(model space), the left ones at +X."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_2.glacier_colossus import (  # noqa: E402
    COLOSSUS_CELLS,
    COLOSSUS_CUTTER_LASER,
    COLOSSUS_ORE_GUNS,
)
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.mini_boss_greebles import vent  # noqa: E402
from game.view.bosses.mini_boss_mechanism import GEAR, cog  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    WHITE,
    H,
    neon_band,
    offset,
    scaled,
)
from game.view.bosses.world_2.avalanche_frost import (  # noqa: E402
    PACKED,
    barrel_to,
    icicles,
    snow_cap,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    gland,
)
from game.view.enemies.enemy_shapes import POD_SECTION, side_stripe  # noqa: E402
from render.geometry.organic import RibSpec, organ, ribs  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# The Glacier Colossus's red-orange neon (P08-R10).
_COLOSSUS_NEON = BOSS_LOOK.neon["glacier-colossus"]
COLOSSUS_NEON = [1.0, 0.35, 0.08] if _COLOSSUS_NEON == None else _COLOSSUS_NEON  # noqa: E711

# The side of a section that faces the nose or the tail, painted with the frost.
POD_BACK = 2
# A cutter's pod along Z around its centre (loft stations: z, half width, bottom, top).
CUTTER_POD = [
    [-20.0, 5.0, -3.0, 6.0],
    [-12.0, 9.0, -5.0, 10.0],
    [12.0, 9.0, -5.0, 10.0],
    [24.0, 6.0, -2.0, 8.0],
]
# The heat sink's base around its centre, and the height of its fins.
SINK_BASE = [
    [-17.0, -12.0],
    [17.0, -12.0],
    [15.0, 13.0],
    [8.0, 17.0],
    [-8.0, 17.0],
    [-15.0, 13.0],
]
FIN_HEIGHT = 9
# The number of rows of fins on the heat sink.
FIN_COUNT = 6


def _octagon() -> list[OutlinePoint]:
    """An octagon of radius 1, flat side to the front."""
    points: list[OutlinePoint] = []
    for k in range(8):
        a = (2 * math.pi * (k + 0.5)) / 8
        points.append([math.sin(a), math.cos(a)])
    return points


OCTAGON = _octagon()


def _sign(x: float) -> float:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def sided(at: Vec3, left: list[Any]) -> list[Any]:
    """Which of two mirrored muzzle lists belongs to the part drawn at `at` (left at +X)."""
    return left if at[0] > 0 else mirror(left)


def cutter_mount(p: EnemyParts, at: Vec3) -> None:
    """The mount a cutter turns on (phase 8 review: the cutter, `cutter`, is its turret and
    aims its laser): a drum under its pod, ringed with neon."""
    # P16-R06: a shoulder of muscle the cutter limb turns on.
    p.flesh.cylinder(8, 3, 7, ICE_FLESH.purple, Placement(offset(at, 0, -7.5, 0)), 7)
    p.neon.ring(8.3, 0.6, 8, COLOSSUS_NEON, Placement(offset(at, 0, -5, 0)))


def cutter(p: EnemyParts, at: Vec3) -> None:
    """A cutter laser (P08-R10), turning on its mount (its turret): a long pod out on the beam,
    a red-orange stripe along its sides, its emitter at the front, a saw disc at its flank,
    frost on its back."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    s = _sign(at[0])
    # P16-R06: a limb of flesh, an armour plate on its back, the laser and saw grafted on.
    flesh.loft(
        POD_SECTION,
        CUTTER_POD,
        ICE_FLESH.sinew,
        Placement(at),
        LoftOptions(
            False,
            lambda side, band: ICE_FLESH.teal if side == POD_BACK else None,
        ),
    )
    for side in [1, 3]:
        stripe = side_stripe(POD_SECTION, side, [0.3, 0.7])
        neon.loft(stripe, CUTTER_POD[1:3], COLOSSUS_NEON, Placement(at), LoftOptions(True))
    tips = sided(at, COLOSSUS_CUTTER_LASER)
    if len(tips) > 0:
        barrel_to(p, tips[0], [2.8, 9], "laser")
    tip = tips[0] if len(tips) > 0 else [0, 0, 0]
    aim = boss_point(tip[0], tip[1], tip[2])
    neon.ring(
        3.6,
        0.8,
        6,
        COLOSSUS_NEON,
        Placement(offset(aim, 0, 0, -6), 0, math.pi / 2),
    )
    cog(hull, offset(at, s * 9.5, 2, 6), 6, 10)
    cap = [[-3.5, -16.0], [3.5, -14.0], [4.0, 6.0], [-3.0, 9.0]]
    snow_cap(
        flesh,
        [[at[0] + q[0], at[2] + q[1]] for q in cap],
        at[1] + 9.6,
        0.8,
    )
    icicles(flesh, [offset(at, 5, -2.5, -8), offset(at, -5, -2.5, 0), offset(at, 5, -2.5, 10)], 4)


def ore_cannon(p: EnemyParts, at: Vec3) -> None:
    """An ore cannon (P08-R10): an armoured octagonal barbette, its housing with two fat barrels
    that fire fans of big shells, a red-orange ring round its foot, snow on its roof."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: an armoured growth, a swollen organ under a metal casemate.
    organ(flesh, 13, 8, ICE_FLESH.purple, Placement(offset(at, 0, 2, 0)), 0.45)
    hull.bevel_slab(
        scaled(OCTAGON, 9),
        [12, 13.5, 15],
        [0, 1.2],
        H.base,
        Placement(at),
        H.panel,
    )
    neon_band(
        neon,
        scaled(OCTAGON, 13),
        [6.5, 8.5],
        [1.02, 1.02],
        COLOSSUS_NEON,
        Placement(at),
    )
    hull.box([16, 6, 14], H.panel, Placement(offset(at, 0, 9, 4)), H.base)
    for tip in sided(at, COLOSSUS_ORE_GUNS):
        barrel_to(p, tip, [2.6, 12])
        q = boss_point(tip[0], tip[1], tip[2])
        hull.cylinder(3.4, 3, 6, GEAR, Placement([q[0], q[1], q[2] - 13], 0, math.pi / 2))
    cap = [[-6.0, -2.0], [5.0, -4.0], [7.0, 6.0], [-5.0, 8.0]]
    snow_cap(flesh, [[at[0] + q[0], at[2] + q[1]] for q in cap], 15, 1)
    gland(p, offset(at, 0, 9, -11), 1.6, COLOSSUS_NEON)


def heat_sink(p: EnemyParts, at: Vec3) -> None:
    """The heat sink (P08-R10, no weapon): a radiator block at the bow, its fins glowing
    red-orange between them; the ice around it has melted, the frost only on its outer rims."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    # P16-R06: a gill organ, its fleshy lamellae glowing between them.
    flesh.bevel_slab(
        SINK_BASE,
        [8, 10, 12],
        [0, 1.2],
        ICE_FLESH.crimson,
        Placement(at),
        ICE_FLESH.purple,
    )
    for i in range(FIN_COUNT):
        z = -9 + i * 4.4
        flesh.box(
            [26 - abs(i - 2.5) * 2, FIN_HEIGHT, 1.4],
            ICE_FLESH.membrane,
            Placement(offset(at, 0, 12, z)),
            ICE_FLESH.sinew,
        )
        if i < FIN_COUNT - 1:
            neon.box(
                [22 - abs(i - 2) * 2, FIN_HEIGHT - 2, 1.6],
                COLOSSUS_NEON,
                Placement(offset(at, 0, 12, z + 2.2)),
            )
    charge.box([6, 0.6, 20], WHITE, Placement(offset(at, 0, 12 + FIN_HEIGHT, 2)))
    for s in [-1, 1]:
        hull.box(
            [3, FIN_HEIGHT + 2, 26],
            H.dark,
            Placement(offset(at, s * 14.5, 12, 2)),
            H.panel,
        )
    icicles(
        flesh,
        [
            offset(at, -15, 8, 14),
            offset(at, 15, 8, 14),
            offset(at, -12, 8, 17),
            offset(at, 12, 8, 17),
        ],
        4,
    )


def missile_pod(p: EnemyParts, at: Vec3) -> None:
    """The missile pod (P08-R10): an armoured box on the stern, four missile tips standing in
    their tubes (they light up as a salvo charges), vents and frost on its back."""
    hull = p.hull
    flesh = p.flesh
    charge = p.charge
    muzzle = p.muzzle
    box_outline: list[OutlinePoint] = [
        [-12.0, -11.0],
        [12.0, -11.0],
        [13.0, 8.0],
        [9.0, 12.0],
        [-9.0, 12.0],
        [-13.0, 8.0],
    ]
    # P16-R06: a brood sac on the stern, four metal tubes grafted in it, missiles growing inside.
    flesh.bevel_slab(
        box_outline,
        [15, 17, 22],
        [0, 3],
        ICE_FLESH.membrane,
        Placement(at),
        ICE_FLESH.purple,
    )
    ribs(
        flesh,
        [at[2] - 6, at[2] + 6],
        RibSpec(13, 16, 6, 0.8),
        ICE_FLESH.bone,
        Placement([at[0], 0, 0]),
    )
    for cell in COLOSSUS_CELLS:
        tip = boss_point(cell[0], cell[1], cell[2])
        hull.ring(2.6, 1, 6, H.dark, Placement(offset(tip, 0, -2.8, 0)))
        charge.cylinder(1.9, 2.6, 6, WHITE, Placement(offset(tip, 0, -2.6, 0)), 0)
        muzzle(tip, "missile")
    vent(hull, offset(at, 0, 21.8, -8.5), [10, 3], 3)
    cap = [[-12.0, 4.0], [-6.0, 2.0], [-5.0, 11.0], [-9.0, 12.0]]
    snow_cap(
        flesh,
        [[at[0] + q[0], at[2] + q[1]] for q in cap],
        22,
        0.8,
        PACKED,
    )
