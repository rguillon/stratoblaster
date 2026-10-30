"""The Ice Queen's crystals: its shards (the parts on its crown ring), the crystals growing on its
wings and ring, its icicles, ported from `bosses/world-2/ice-queen-shards.ts`. Logical pixels,
nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H
from game.view.bosses.world_2.w2_organic import ICE_FLESH
from render.geometry.organic import organ
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.entities.muzzle import Muzzle  # noqa: E402
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

_ICE_QUEEN_NEON = BOSS_LOOK.neon["ice-queen"]
# Pale blue: the Ice Queen's registered neon (GD-61).
PALE_BLUE = WHITE if _ICE_QUEEN_NEON == None else _ICE_QUEEN_NEON  # noqa: E711
# Violet: the Ice Queen's second neon colour, on its edges (P08-R10).
VIOLET = [0.62, 0.3, 1]

# World 2 frost (P08-R10): snow on top faces, pale faceted ice (the palest at the facets' tips),
# frosted (snow-dusted) panels.
FROST = record(
    {
        "snow": [0.75, 0.82, 0.9],
        "ice": [0.56, 0.7, 0.92],
        "pale": [0.84, 0.92, 1],
        "frosted": [0.36, 0.4, 0.47],
    }
)

# A crystal's faceted body (a lathe profile, in units of its radius and length).
CRYSTAL = [  # type: list[list[float]]
    [0.6, 0],
    [1, 0.3],
    [0.8, 0.72],
]
CRYSTAL_TIP = [  # type: list[list[float]]
    [0.8, 0.72],
    [0, 1],
]


def _scaled(profile: list[list[float]], radius: float, length: float) -> list[list[float]]:
    """A lathe profile in units of a radius and a length, in model units."""
    return [[p[0] * radius, p[1] * length] for p in profile]


def crystal(hull: SolidBuilder, at: Vec3, angles: list[float], dims: list[float]) -> None:
    """A six-sided crystal growing from `at`, `dims[0]` thick and `dims[1]` long, tilted by
    `angles` = `[pitch, roll, yaw]` from straight up: blue ice, its tip the palest."""
    place = Placement(at, angles[2], angles[0], angles[1])
    hull.lathe(_scaled(CRYSTAL, dims[0], dims[1]), 6, FROST.ice, place)
    hull.lathe(_scaled(CRYSTAL_TIP, dims[0], dims[1]), 6, FROST.pale, place, False)


def icicles(hull: SolidBuilder, s: float, points: list[list[float]]) -> None:
    """Icicles hanging under a wing on side `s`, at the `[x, z]` given (x for the right wing)."""
    for i in range(len(points)):
        x = points[i][0]
        z = points[i][1]
        place = Placement([s * x, 0.2, z], 0, math.pi)
        hull.cylinder(0.7, 2.5 + (i % 3) * 1.2, 4, FROST.ice, place, 0)


# A shard lies between two muzzles.
SHARD_MUZZLES = 2

# A shard's body along its axis (a lathe profile: radius, distance from its centre).
SHARD = [  # type: list[list[float]]
    [0, -10.8],
    [2.6, -7],
    [4, -1.5],
    [3.6, 4],
    [2.4, 8.5],
    [0, 10.8],
]
# The pale crystal on its back, the charge light at each tip.
SHARD_RIDGE = [  # type: list[list[float]]
    [0, -6],
    [1.7, 0],
    [0, 6],
]
SHARD_TIP = [  # type: list[list[float]]
    [1.2, 0],
    [0, 2.2],
]


def _axis(centre: Vec3, yaw: float, along: float, up: float, turn: float) -> Placement:
    """A placement on the shard's axis, `along` from its centre, `up` higher, turned `turn`."""
    at: Vec3 = [
        centre[0] + math.sin(yaw) * along,
        centre[1] + up,
        centre[2] + math.cos(yaw) * along,
    ]
    return Placement(at, turn, QUARTER, 0)


def ice_shard(p: EnemyParts, muzzles: list[Muzzle], height: float) -> None:
    """P08-R10: a crystal shard on the crown ring, lying along the ring between its two `muzzles`
    (from the design, `height` high): faceted ice banded with violet neon, a light at each tip
    where its bullets leave, a pale spike pointing out of the ring, a dark clamp under it."""
    points: list[Vec3] = [boss_point(m[0], m[1], m[2]) for m in muzzles]
    if len(points) < SHARD_MUZZLES:
        return
    a = points[0]
    b = points[1]
    centre: Vec3 = [(a[0] + b[0]) / 2, height, (a[2] + b[2]) / 2]
    yaw = math.atan2(b[0] - a[0], b[2] - a[2])
    p.hull.lathe(SHARD, 6, FROST.ice, _axis(centre, yaw, 0, 0, yaw))
    p.hull.lathe(SHARD_RIDGE, 4, FROST.pale, _axis(centre, yaw, 0, 3.4, yaw))
    p.neon.ring(4.1, 0.9, 6, VIOLET, _axis(centre, yaw, -1.9, 0, yaw))
    p.charge.lathe(SHARD_TIP, 4, WHITE, _axis(centre, yaw, 10.8, 0, yaw))
    p.charge.lathe(SHARD_TIP, 4, WHITE, _axis(centre, yaw, -10.8, 0, yaw + math.pi))
    p.muzzle(a, "gun")
    p.muzzle(b, "gun")
    # P16-R05: each crystal is grown from a sac of flesh, held to the ring by a metal clamp.
    organ(
        p.flesh,
        4.5,
        6,
        ICE_FLESH.purple,
        Placement([centre[0], height - 5, centre[2]], yaw),
        0.5,
    )
    p.hull.box([5, 1.2, 3], H.dark, Placement([centre[0], height - 5.2, centre[2]], yaw))
    out = math.atan2(centre[0], centre[2])
    spike: Vec3 = [
        centre[0] + math.sin(out) * 2.5,
        height + 1.5,
        centre[2] + math.cos(out) * 2.5,
    ]
    crystal(p.hull, spike, [1, 0, out], [1.5, 6.5])
