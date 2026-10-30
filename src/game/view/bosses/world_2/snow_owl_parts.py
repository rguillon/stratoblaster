"""The Snow Owl's parts (its radar pods and sensor eye) and its frost (P08-R10, 2-3). Logical
pixels, nose +Z, Y up (towards the
camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_2.snow_owl import OWL_EYE_LENS, OWL_POD_GUNS
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset
from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals, gland
from game.view.enemies.enemy_shapes import POD_SECTION, SIDES
from render.geometry.solids import Placement, place_at

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

_OWL_NEON = BOSS_LOOK.neon["snow-owl"]
# The Snow Owl's white neon.
OWL_WHITE = [0.85, 0.92, 1] if _OWL_NEON == None else _OWL_NEON  # noqa: E711
# Snow lying on its top faces, and the bluer ice of its crust and icicles (World 2 frost).
FROST = [0.75, 0.82, 0.9]
ICE = ICE_FLESH.crystal

# A radar pod's nacelle under its radome (loft stations around the pod's centre).
NACELLE = [
    [-11, 4, -3, 3],
    [-4, 5.5, -3.5, 4],
    [8, 5, -3, 3.5],
    [13, 3.5, -1.5, 2.5],
]
# A pod's radome: an iced dome on the wing (a lathe profile).
RADOME = [
    [7, 1.6],
    [7.2, 3],
    [5.8, 5.2],
    [3, 6.8],
    [0, 7.2],
]


def _sign(x: float) -> float:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def icicles(hull: SolidBuilder, points: list[Vec3], side: float = 1) -> None:
    """Icicles hanging from each point (`[x, y, z]`, `x` times `side`): thin cones of ice."""
    for i in range(len(points)):
        x = points[i][0]
        y = points[i][1]
        z = points[i][2]
        length = 3.5 + (i % 3) * 1.2
        hull.cylinder(0.9, length, 4, ICE, Placement([side * x, y, z], 0, math.pi), 0)


def radar_pod(p: EnemyParts, at: Vec3) -> None:
    """A wing radar pod around its centre `at` (P08-R10): a nacelle under an iced radome with a
    turning antenna on top, and two fan barrels poking out of the nacelle's front."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    s = _sign(at[0])
    # P16-R05: a swollen nacelle of flesh, the radome a metal graft on it.
    p.flesh.loft(POD_SECTION, NACELLE, ICE_FLESH.purple, Placement([at[0], 0, at[2]]))
    gland(p, offset(at, -s * 4, 3.6, 8), 0.9, OWL_WHITE)
    hull.lathe(RADOME, 8, FROST, Placement(offset(at, 0, 0, -2), math.pi / 8))
    neon.ring(7.3, 0.6, 8, OWL_WHITE, Placement(offset(at, 0, 2, -2), math.pi / 8))
    p.rotor(offset(at, 0, 7.4, -2), 6.5)
    hull.box([3, 1, 5], SHADE["edge"], Placement(offset(at, s * 4.5, 3.4, -9)))
    icicles(p.flesh, [offset(at, 3, -3, -6), offset(at, -3, -3, -3)])
    # The right pod (screen right) is on the model's -X side.
    guns = OWL_POD_GUNS if s < 0 else mirror(OWL_POD_GUNS)
    for m in guns:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(1.2, 6.4, 6, H.dark, Placement([x, y, z - 7], 0, QUARTER))
        charge.cylinder(1.25, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip, "gun")


def eye(p: EnemyParts, at: Vec3) -> None:
    """The sensor eye around its centre `at` (P08-R10): a big round housing facing forward, its
    lens ringed with white neon, the iris lighting up as its laser charges, under a snow-capped
    brow."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    lenses: list[Vec3] = [boss_point(m[0], m[1], m[2]) for m in OWL_EYE_LENS]
    if len(lenses) == 0:
        return
    lens = lenses[0]
    x = lens[0]
    y = lens[1]
    z = lens[2]
    forward = Placement(None, 0, QUARTER, 0)
    # P16-R05: a real eye, its lid of flesh, a bone brow over it.
    p.flesh.cylinder(
        9.5,
        9,
        10,
        ICE_FLESH.sinew,
        place_at(forward, [x, y, z - 10.5]),
        9,
    )
    neon.ring(9.7, 0.8, 10, OWL_WHITE, place_at(forward, [x, y, z - 2.3]))
    neon.cylinder(7.5, 0.8, 10, OWL_WHITE, place_at(forward, [x, y, z - 1.5]))
    hull.cylinder(5.4, 0.3, 10, H.dark, place_at(forward, [x, y, z - 0.7]))
    charge.cylinder(3.6, 0.7, 8, WHITE, place_at(forward, [x, y, z - 0.7]))
    muzzle(lens, "laser")
    p.flesh.box(
        [22, 2.2, 7],
        ICE_FLESH.bone,
        Placement(offset(at, 0, 14.5, 1), 0, -0.12, 0),
        ICE_FLESH.rime,
    )
    icicles(
        p.flesh,
        [offset(at, 6, 14.6, 4), offset(at, -1, 14.6, 4.3), offset(at, -7, 14.6, 4)],
    )
    for s in SIDES:
        p.flesh.box(
            [1.4, 7, 8],
            ICE_FLESH.purple,
            Placement(offset(at, s * 10.4, 2.5, 0)),
            ICE_FLESH.rime,
        )
        crystals(p.flesh, offset(at, s * 9, 13, -2), 3, 2)
        neon.box([0.5, 0.5, 6], OWL_WHITE, Placement(offset(at, s * 11.2, 8.6, 0)))
