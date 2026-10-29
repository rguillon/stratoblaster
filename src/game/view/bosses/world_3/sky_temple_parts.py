"""P09-R09, 3-3: the Sky Temple's parts (its corner obelisks, its summit beacon). Ported from
`view/bosses/world-3/sky-temple-parts.ts`. Logical pixels, nose +Z (its grand stair, down the
screen), Y up (towards the camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.world_3.sky_temple import TEMPLE_BEACON, TEMPLE_HEIGHTS
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_shapes import missile_tips
from game.view.bosses.mini_boss_shapes import WHITE, offset
from game.view.bosses.world_3.jungle_flesh import sign_of
from game.view.bosses.world_3.stone_idol_stone import STONE, moss, vine
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The Sky Temple's gold neon, and the cyan it shares its lights with (P09-R09).
TEMPLE_GOLD = BOSS_LOOK.neon["sky-temple"]
TEMPLE_CYAN = [0.2, 0.95, 1]
# An eighth of a turn: four-sided solids turned square to the axes.
SQUARE = math.pi / 4
# The pyramid's tiers: half widths (the base first) and their common height.
TIERS = record({"halves": [74, 54, 44, 34], "height": 9})
# The height of the summit platform.
SUMMIT = len(TIERS.halves) * TIERS.height

# Heights of an obelisk: its plinth's top, its shaft's top (its pyramidion ends at its tip).
OBELISK = record({"plinth": TIERS.height + 4, "shaft": TEMPLE_HEIGHTS.obelisk - 7})


def corner(half: float) -> float:
    """A four-sided solid's corner radius for a half width `half`."""
    return half * math.sqrt(2)


def obelisk(p: EnemyParts, at: Vec3) -> None:
    """A corner obelisk around its centre `at` (P09-R09): a plinth on the lowest tier, a tapering
    stone shaft carved with gold glyphs, a gilt pyramidion whose tip fires its spirals, a vine
    climbing it."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    hull.box(
        [12, 4, 12],
        STONE.dark,
        Placement(offset(at, 0, TIERS.height, 0)),
        STONE.light,
    )
    neon.ring(
        corner(6.1),
        0.6,
        4,
        TEMPLE_CYAN,
        Placement(offset(at, 0, OBELISK.plinth - 0.8, 0), SQUARE),
    )
    base = 4
    top = 2.9
    height = OBELISK.shaft - OBELISK.plinth
    hull.cylinder(
        corner(base),
        height,
        4,
        STONE.base,
        Placement(offset(at, 0, OBELISK.plinth, 0), SQUARE),
        corner(top),
    )
    tip_height = TEMPLE_HEIGHTS.obelisk - OBELISK.shaft
    hull.cylinder(
        corner(top + 0.3),
        tip_height,
        4,
        STONE.gilt,
        Placement(offset(at, 0, OBELISK.shaft, 0), SQUARE),
        0,
    )
    charge.ring(
        corner(top + 0.35),
        1.2,
        4,
        WHITE,
        Placement(offset(at, 0, OBELISK.shaft + 0.2, 0), SQUARE),
    )
    muzzle(offset(at, 0, TEMPLE_HEIGHTS.obelisk, 0), "ring")
    # Gold glyphs on its four faces, at three heights (each just proud of the tapering face).
    for k in [0.15, 0.45, 0.75]:
        y = OBELISK.plinth + height * k
        half = base + (top - base) * k + 0.15
        for s in SIDES:
            neon.box([1.8, 1.4, 0.3], TEMPLE_GOLD, Placement(offset(at, 0, y, s * half)))
            neon.box([0.3, 1.4, 1.8], TEMPLE_GOLD, Placement(offset(at, s * half, y, 0)))
    s = sign_of(at[0])
    vine(
        hull,
        [
            offset(at, s * 6, TIERS.height + 4, 4),
            offset(at, s * 4.4, 16, 3),
            offset(at, s * 3.6, 22, -2),
            offset(at, s * 3.2, 27, 1),
        ],
    )
    moss(hull, offset(at, -s * 3, OBELISK.plinth, -4), 2.6, s)


# The beacon's lantern: its tower's top, and its roof (under the missile tubes).
LANTERN = record({"base": SUMMIT + 10, "roof": SUMMIT + 13})


def beacon(p: EnemyParts, at: Vec3) -> None:
    """The summit beacon around its centre `at` (P09-R09): a square tower at the front of the
    summit, a lantern burning cyan under a gilt roof, four missile tubes on the roof."""
    hull = p.hull
    neon = p.neon
    hull.box(
        [12, LANTERN.base - SUMMIT, 12],
        STONE.base,
        Placement(offset(at, 0, SUMMIT, 0)),
        STONE.light,
    )
    neon.ring(
        corner(6.1),
        0.6,
        4,
        TEMPLE_GOLD,
        Placement(offset(at, 0, LANTERN.base - 1.6, 0), SQUARE),
    )
    lantern = LANTERN.roof - LANTERN.base
    neon.box([7, lantern, 7], TEMPLE_CYAN, Placement(offset(at, 0, LANTERN.base, 0)))
    for x in SIDES:
        for z in SIDES:
            hull.box(
                [1.6, lantern, 1.6],
                STONE.dark,
                Placement(offset(at, x * 5, LANTERN.base, z * 5)),
            )
    tubes = [boss_point(m[0], m[1], m[2]) for m in TEMPLE_BEACON]
    radius = 1.5
    # The tubes' tips stand `2.6 radius` above their foot (see `missileTips`).
    first_y = tubes[0][1] if len(tubes) > 0 else TEMPLE_HEIGHTS.beacon
    foot = first_y - radius * 2.6
    hull.box(
        [13, foot - LANTERN.roof, 13],
        STONE.gilt,
        Placement(offset(at, 0, LANTERN.roof, 0)),
    )
    missile_tips(p, [at[0], foot, at[2]], [2, 2], [6, radius])
    moss(hull, offset(at, 4, SUMMIT, -7), 2.4, 2)
