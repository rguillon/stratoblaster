"""P08-R10, 2-3: the Aurora Station's parts (dish emitters, cryo cannons, drone hangar), its
turning dish and its frost, ported from `bosses/world-2/aurora-station-parts.ts`. Logical
pixels, nose +Z, Y up (towards the camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_2.aurora_station import AURORA_EMITTER  # noqa: E402
from game.config.record import record  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.mini_boss_greebles import (  # noqa: E402
    lamps,
    plate,
    rect,
)
from game.view.bosses.mini_boss_mechanism import conduit  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
    turret,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    gland,
)
from game.view.enemies.enemy_shapes import POD_SECTION, SIDES  # noqa: E402
from render.geometry.organic import RibSpec, organ, ribs  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# The Aurora Station's green neon, and the violet one it shares its lights with.
_AURORA_NEON = BOSS_LOOK.neon["aurora-station"]
AURORA_GREEN = [0.3, 1.0, 0.55] if _AURORA_NEON == None else _AURORA_NEON  # noqa: E711
AURORA_VIOLET = [0.62, 0.3, 1.0]
# Snow lying on its top faces, and the bluer ice of its crust and icicles (World 2 frost).
FROST = [0.75, 0.82, 0.9]
ICE = ICE_FLESH.crystal

# A side of a section that faces the nose or the tail, painted with the rime (`iced`).
POD_BACK = 2
# The dish's tilt: it looks up and forward, and turns with the boss's spin.
DISH_TILT = 0.6


def _sign(x: float) -> float:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def icicles(hull: SolidBuilder, points: Sequence[Vec3], side: float = 1) -> None:
    """Icicles hanging from each point (`[x, y, z]`, `x` times `side`): thin cones of ice."""
    for i, point in enumerate(points):
        length = 3.5 + (i % 3) * 1.3
        hull.cylinder(
            0.9,
            length,
            4,
            ICE,
            Placement([side * point[0], point[1], point[2]], 0, math.pi),
            0,
        )


def bowl(r: float) -> list[Vec3]:
    """A dish: a shallow bowl `r` wide around its axis (a lathe profile)."""
    return [
        [0.4, 0.0],
        [r, r * 0.35],
        [r * 0.8, r * 0.45],
        [0.0, r * 0.2],
    ]


def emitter(p: EnemyParts, at: Vec3) -> None:
    """A dish emitter's pylon around its centre `at` (P08-R10): its dish turns on it."""
    # P16-R06: a swollen node of flesh at the end of its arm, a metal socket for the dish.
    organ(p.flesh, 7, 6, ICE_FLESH.purple, Placement(offset(at, 0, -2, -3)), 0.5)
    p.hull.box([4, 6, 5], H.panel, Placement(offset(at, 0, 2, -3)), H.base)
    gland(p, offset(at, _sign(at[0]) * 5, 2, -6), 1, AURORA_GREEN)


def emitter_turret(p: EnemyParts, at: Vec3) -> None:
    """A dish emitter's turret, turning on its pylon (phase 8 review: it aims its laser): an
    upright dish facing down the screen, struts holding its projector at the focus, where the
    laser leaves from."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    # The right emitter (screen right) is on the model's -X side.
    lasers = AURORA_EMITTER if at[0] < 0 else mirror(AURORA_EMITTER)
    tips = [boss_point(m[0], m[1], m[2]) for m in lasers]
    if len(tips) == 0:
        return
    tip = tips[0]
    x = tip[0]
    y = tip[1]
    z = tip[2]
    hull.lathe(bowl(9), 10, SHADE.edge, Placement([x, y, z - 15], 0, QUARTER))
    neon.ring(9.1, 0.6, 10, AURORA_VIOLET, Placement([x, y, z - 12.2], 0, QUARTER))
    hull.cylinder(1.4, 10, 6, H.dark, Placement([x, y, z - 11], 0, QUARTER))
    neon.ring(1.8, 0.6, 6, AURORA_GREEN, Placement([x, y, z - 5], 0, QUARTER))
    charge.cylinder(2, 1, 8, WHITE, Placement([x, y, z - 1], 0, QUARTER))
    muzzle(tip, "laser")
    for d in [[7.5, -2], [-7.5, -2], [0, 8.5]]:
        conduit(hull, [x + d[0], y + d[1], z - 12], [x, y, z - 3], 0.4, 0)
    # Snow caught on the dish's top rim, icicles under its lower rim.
    hull.box([8, 1, 2.4], FROST, Placement([x, y + 8.6, z - 12.4]))
    icicles(
        p.flesh,
        [[x + 4, y - 7.5, z - 12], [x - 3, y - 8.3, z - 12]],
    )


# A cryo cannon's tank (loft stations around the part's centre), its top iced over.
TANK = [
    [-20.0, 6.0, -4.0, 4.0],
    [-12.0, 12.0, -5.0, 6.0],
    [6.0, 12.0, -5.0, 6.0],
    [14.0, 7.0, -3.0, 4.0],
]


def iced(side: float) -> Rgb | None:
    """Ice on the top of a `POD_SECTION` loft (its side 2)."""
    if side == POD_BACK:
        rime: Rgb = ICE_FLESH.rime
        return rime
    return None


def cryo_cannon(p: EnemyParts, at: Vec3) -> None:
    """A cryo cannon's body around its centre `at` (P08-R10): a cryogenic tank on the station's
    truss, iced over, two coolant flasks behind its turret (`cryo_turret`)."""
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a cryo bladder of flesh, rimed over, two glands of coolant behind its gun.
    flesh.loft(
        POD_SECTION,
        TANK,
        ICE_FLESH.teal,
        Placement([at[0], 0, at[2]]),
        LoftOptions(False, lambda side, band: iced(side)),
    )
    ribs(
        flesh,
        [at[2] - 8, at[2]],
        RibSpec(12, -2, 7, 0.7),
        ICE_FLESH.bone,
        Placement([at[0], 0, 0]),
    )
    for s in SIDES:
        flask = offset(at, s * 6, 6, -14)
        organ(flesh, 3.6, 6, ICE_FLESH.membrane, Placement(flask), 0.7)
        neon.ring(3.7, 0.6, 8, AURORA_VIOLET, Placement(offset(flask, 0, 2, 0)))
        neon.box([0.6, 0.4, 14], AURORA_GREEN, Placement(offset(at, s * 12.3, 1, -3)))
    icicles(
        flesh,
        [offset(at, 6, -4, 9), offset(at, -2, -4.5, 10), offset(at, -8, -4, 6)],
    )


def cryo_turret(p: EnemyParts, at: Vec3) -> None:
    """A cryo cannon's turret: a single wide-bored barrel, a violet ring round its foot."""
    turret(
        p,
        offset(at, 0, 6, 0),
        record(
            {
                "radius": 11,
                "barrels": 1,
                "gap": 0,
                "bore": 2.6,
                "length": 9,
                "neon": AURORA_VIOLET,
                "hatch": -_sign(at[0]),
            }
        ),
    )


def hangar(p: EnemyParts, at: Vec3) -> None:
    """The drone hangar around its centre `at` (P08-R10): a snow-roofed bay at the station's
    nose, its open door framed in violet, where its Hornets leave from."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a brood pouch of flesh at the nose, its mouth framed in violet.
    flesh.bevel_slab(
        rect(26, 24),
        [-3, 0, 8],
        [1, 3],
        ICE_FLESH.sinew,
        Placement(at),
        ICE_FLESH.rime,
    )
    flesh.box([18, 7, 0.8], ICE_FLESH.seam, Placement(offset(at, 0, -1.5, 11.8)))
    neon.box([20, 0.8, 0.6], AURORA_VIOLET, Placement(offset(at, 0, 5.6, 12.2)))
    for s in SIDES:
        neon.box([0.8, 7, 0.6], AURORA_VIOLET, Placement(offset(at, s * 9.8, -1.4, 12.2)))
        lamps(
            neon,
            [offset(at, s * 11, 8, 9), offset(at, s * 11, 8, -9)],
            1.2,
            AURORA_GREEN,
        )
    plate(hull, rect(10, 6), [8, 0.8], H.panel, Placement(offset(at, 0, 0, -4)))
    crystals(flesh, offset(at, -8, 8, 2), 3.5)
    icicles(
        flesh,
        [offset(at, 6, 5.5, 12.4), offset(at, 0, 5.5, 12.4), offset(at, -6, 5.5, 12.4)],
    )


def dish(p: EnemyParts) -> None:
    """The big dish on top (P08-R10), drawn on the model's ring so that it turns slowly: a
    snow-filled bowl on a turntable, a violet rim, and its feed horn lit green at the focus."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon

    def axis(along: float) -> Vec3:
        return [0, 19 + along * math.cos(DISH_TILT), along * math.sin(DISH_TILT)]

    # P16-R06: the crown, a frilled bowl of membrane turning on its stalk.
    hull.cylinder(4, 2, 8, H.panel, Placement([0, 17, 0]))
    flesh.lathe(bowl(15), 12, ICE_FLESH.membrane, Placement(axis(0), 0, DISH_TILT))
    neon.ring(15.1, 0.6, 12, AURORA_VIOLET, Placement(axis(4.9), 0, DISH_TILT))
    flesh.cylinder(0.9, 10, 4, ICE_FLESH.sinew, Placement(axis(0), 0, DISH_TILT))
    neon.box([2.2, 2.2, 2.2], AURORA_GREEN, Placement(axis(10), 0, DISH_TILT))
    hull.box([5, 4, 3], H.base, Placement([0, 15.5, -4]), SHADE.edge)
