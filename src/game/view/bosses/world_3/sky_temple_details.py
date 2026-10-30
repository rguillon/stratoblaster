"""P09-R09, 3-3: the Sky Temple's dressing (phase 7 review: detail and some asymmetry; World 3
theme: dark metal with neon, plus moss, vines and stone). Logical pixels, nose +Z, Y up."""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import record
from game.view.bosses.mini_boss_greebles import lamps
from game.view.bosses.mini_boss_shapes import QUARTER, H
from game.view.bosses.world_3.jungle_flesh import table
from game.view.bosses.world_3.sky_temple_flesh import temple_reactors
from game.view.bosses.world_3.sky_temple_parts import SUMMIT, TEMPLE_CYAN, TEMPLE_GOLD, TIERS
from game.view.bosses.world_3.stone_idol_stone import STONE, leaf, moss, vine
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The thrusters' bank behind the pyramid: its centre along Z, and its nozzles across.
THRUSTERS = record({"z": -81, "nozzles": [-22, 0, 22]})


def temple_machinery(p: EnemyParts) -> None:
    """The fortress under the stones: a bank of thrusters at the back, and armoured buttresses on
    the sides with gold and cyan lights."""
    hull = p.hull
    neon = p.neon
    hull.box([66, 12, 14], H.base, Placement([0, -6, THRUSTERS.z]), H.panel)
    neon.box([60, 0.6, 0.5], TEMPLE_CYAN, Placement([0, 4, THRUSTERS.z - 7.1]))
    for x in THRUSTERS.nozzles:
        hull.cylinder(
            5.4,
            3,
            8,
            H.dark,
            Placement([x, 0, THRUSTERS.z - 7], 0, -QUARTER),
        )
    temple_reactors(p, THRUSTERS.z - 7.4, THRUSTERS.nozzles)
    base = TIERS.halves[0]
    for s in SIDES:
        hull.box([6, 11, 44], H.base, Placement([s * (base + 2.4), -6, -6]), H.panel)
        neon.box([0.5, 0.6, 38], TEMPLE_GOLD, Placement([s * (base + 5.5), 2, -6]))
        lamps(
            neon,
            [[s * (base + 2.4), 5, 18], [s * (base + 2.4), 5, -30]],
            1.4,
            TEMPLE_CYAN,
        )


# Moss patches on the tiers' steps (x, z, which tier's top, size).
MOSS = table(
    [
        [-48, 64, 1, 5],
        [62, 30, 1, 4],
        [-64, -20, 1, 4.5],
        [30, -62, 1, 5],
        [-49, -30, 2, 3.5],
        [48, 30, 2, 3],
        [-24, 40, 3, 3.2],
        [20, -30, 4, 3],
    ]
)
# Vines draped over a tier's edge: from its top, down its side (x, z on the edge, tier).
DRAPED = table(
    [
        [-30, 1, 0],
        [20, 1, 1],
        [-12, -1, 2],
        [30, 1, 3],
        [-50, -1, 0],
    ]
)
# Roots hanging under the rock's rim, and shrubs grown on the second tier.
ROOTS = table([[40, 70], [-66, 30], [70, -50], [-20, -72]])
SHRUBS = table([[-38, 50], [-30, 52]])


def drape_point(along: float, side: float, half: float, inset: float, y: float) -> Vec3:
    """A point on a tier's edge (`side`: +-1 an east or west edge, 0 the back edge), `inset`
    out from it, at height `y`."""
    if side == 0:
        return [along, y, -half - inset]
    return [side * (half + inset), y, along]


def temple_jungle(p: EnemyParts) -> None:
    """The jungle over the stones: moss on the steps, vines over the edges, shrubs on a tier."""
    hull = p.hull
    for m in MOSS:
        x = m[0]
        z = m[1]
        tier = m[2]
        size = m[3]
        moss(hull, [x, tier * TIERS.height, z], size, x)
    for i in range(len(DRAPED)):
        d = DRAPED[i]
        along = d[0]
        side = d[1]
        tier = d[2]
        half = TIERS.halves[tier] or 74
        top = (tier + 1) * TIERS.height
        # `side`: +-1 an east / west edge (x = +-half, `along` z), 0 the back edge (z = -half).
        vine(
            hull,
            [
                drape_point(along, side, half, -3, top),
                drape_point(along, side, half, 0.4, top - 0.2),
                drape_point(along, side, half, 0.8, top - 4),
                drape_point(along, side, half, 0.6, top - 9 - (i % 3) * 2),
            ],
        )
    # Roots hanging under the rock's rim.
    for r in ROOTS:
        x = r[0]
        z = r[1]
        vine(
            hull,
            [[x, -2, z], [x * 0.96, -10, z * 0.96], [x * 0.9, -18, z * 0.9]],
            1.4,
        )
    # Shrubs grown on the second tier, to the left of the stair.
    for sh in SHRUBS:
        x = sh[0]
        z = sh[1]
        hull.cylinder(3.2, 4.5, 5, STONE.leaf, Placement([x, 2 * TIERS.height, z]), 0.8)
        leaf(hull, [x + 2, 2 * TIERS.height + 1, z - 2], 3.4, x)
    leaf(hull, [10, SUMMIT, -30], 3, 1)
