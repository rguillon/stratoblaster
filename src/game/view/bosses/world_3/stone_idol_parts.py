"""P09-R09, 3-3: the Stone Idol's parts (its eyes, their turning eyeballs, its mouth). Logical
pixels, nose +Z (the chin), Y up (towards the
camera); the face looks up at the camera."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_3.stone_idol import IDOL_EYE, IDOL_THROAT
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    WHITE,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import F, sign_of, table, vein_to
from game.view.bosses.world_3.stone_idol_stone import STONE, crack, moss, vine
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The Stone Idol's neon: the light glowing through its cracks, eyes and mouth.
IDOL_NEON = BOSS_LOOK.neon["stone-idol"]
# Height of the face's carved surface.
FACE = 12

# An eyeball: a polished stone ball (a lathe profile, around its centre's height).
EYEBALL = table([[0, -6.5], [4.6, -4.6], [6.5, 0], [4.6, 4.6], [0, 6.5]])
# The iris's tilt from straight up towards the front (+Z).
IRIS_TILT = QUARTER * 0.55
# The mouth's open lips (outline around its centre: half width, half depth).
LIPS = record({"width": 15, "depth": 8})


def eye_socket(p: EnemyParts, at: Vec3) -> None:
    """An eye's socket around its centre `at` (P09-R09): a deep, round hollow in the face, its rim
    cracked and lit, moss on its lower lid. Its eyeball (`eyeball`) turns in it."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    s = sign_of(at[0])
    # P16-R05: a raw flesh eyelid ringed by a stone growth, veins spreading from its corner.
    hull.cylinder(10.5, 1.6, 10, STONE.dark, Placement(offset(at, 0, FACE - 0.4, 0)), 9.5)
    flesh.cylinder(9, 0.3, 10, F.crimson, Placement(offset(at, 0, FACE + 1, 0)))
    vein_to(
        p,
        [offset(at, -s * 9, FACE + 0.6, -2), offset(at, -s * 15, FACE + 0.4, -9)],
        [0, 0, 2],
        IDOL_NEON,
    )
    neon.ring(9.7, 0.5, 10, IDOL_NEON, Placement(offset(at, 0, FACE + 1.1, 0)))
    # A crack running from the socket's outer corner, and moss on the lower lid.
    x = at[0]
    z = at[2]
    crack(
        neon,
        [[x + s * 9, z + 3], [x + s * 12, z + 8], [x + s * 11, z + 13]],
        FACE + 0.2,
        IDOL_NEON,
    )
    moss(hull, offset(at, -s * 4, FACE + 0.8, 9), 3.2, s)


def iris_point(centre: Vec3, y: float, d: float) -> Vec3:
    """A point `d` along the iris's tilt from `centre`, at height `y`."""
    return [
        centre[0],
        y + d * math.cos(IRIS_TILT),
        centre[2] + d * math.sin(IRIS_TILT),
    ]


def eyeball(p: EnemyParts, at: Vec3) -> None:
    """An eyeball turning in its socket (phase 8 review: it aims its laser): a ball of polished
    stone, a neon iris facing down the screen and the charge-lit lens its laser leaves from."""
    flesh = p.flesh
    vein = p.vein
    charge = p.charge
    muzzle = p.muzzle
    # The right eye (screen right) is on the model's -X side.
    lasers = IDOL_EYE if at[0] < 0 else mirror(IDOL_EYE)
    if len(lasers) == 0:
        return
    tip = boss_point(lasers[0][0], lasers[0][1], lasers[0][2])
    x = tip[0]
    y = tip[1]
    z = tip[2]
    centre: Vec3 = [at[0], y, at[2]]
    # P16-R05: a living, wet eyeball of bone-white flesh, its iris a pulsing gland.
    flesh.lathe(EYEBALL, 8, F.bone, Placement(centre))
    # The glowing iris looks up and forward, half at the camera, half where the eye aims.
    vein.cylinder(4.4, 0.8, 8, IDOL_NEON, Placement(iris_point(centre, y, 6.1), 0, IRIS_TILT), 4)
    flesh.cylinder(2, 0.5, 6, F.purple, Placement(iris_point(centre, y, 6.8), 0, IRIS_TILT))
    charge.cylinder(2.2, 1.6, 8, WHITE, Placement([x, y, z - 1.6], 0, QUARTER), 1.4)
    muzzle(tip, "laser")


def mouth(p: EnemyParts, at: Vec3) -> None:
    """The mouth around its centre `at` (P09-R09): thick carved lips open on a deep throat, stone
    teeth, a neon lining; its rings of boulders leave from the throat's glow."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    w = LIPS.width
    d = LIPS.depth
    # P16-R05: a living maw: a red throat, swollen flesh lips, the stone grown over them as armour.
    flesh.box([w * 2, 0.6, d * 2], F.wound, Placement(offset(at, 0, FACE - 0.2, 0)))
    # Upper lip (towards the nose, -Z), lower lip, and the corners.
    flesh.box(
        [w * 2 + 4, 4, 4],
        F.sinew,
        Placement(offset(at, 0, FACE - 1, -d - 1)),
        F.crimson,
    )
    flesh.box(
        [w * 2, 4.5, 5],
        F.sinew,
        Placement(offset(at, 0, FACE - 1, d + 1.5)),
        F.crimson,
    )
    hull.box(
        [w * 1.2, 1, 2.4],
        STONE.base,
        Placement(offset(at, 0, FACE + 3, -d - 1.6)),
        STONE.light,
    )
    for s in SIDES:
        flesh.box([4, 4, d * 2], F.sinew, Placement(offset(at, s * (w + 1), FACE - 1, 0)))
        neon.box(
            [0.5, 0.5, d * 2 - 1],
            IDOL_NEON,
            Placement(offset(at, s * (w - 1.2), FACE + 0.4, 0)),
        )
    neon.box([w * 2 - 2, 0.5, 0.5], IDOL_NEON, Placement(offset(at, 0, FACE + 0.4, -d + 1.2)))
    neon.box([w * 2 - 2, 0.5, 0.5], IDOL_NEON, Placement(offset(at, 0, FACE + 0.4, d - 1.2)))
    # Stone teeth: square ones under the upper lip, worn ones on the lower.
    for x in [-9, -4.5, 0, 4.5, 9]:
        flesh.box([3, 1.6, 2.6], F.bone, Placement(offset(at, x, FACE, -d + 2.4)))
        if x != 0:
            flesh.box([2.6, 1.2, 2], F.bone, Placement(offset(at, x * 0.9, FACE, d - 2.2)))
    for m in IDOL_THROAT:
        throat = boss_point(m[0], m[1], m[2])
        glow: Vec3 = [throat[0], FACE + 0.1, throat[2]]
        charge.cylinder(5, throat[1] - glow[1], 8, WHITE, Placement(glow), 3)
        muzzle(throat, "ring")
    moss(hull, offset(at, 7, FACE + 3, d + 2), 3, 1)
    # A vine hanging from the lower lip over the chin.
    vine(
        hull,
        [
            offset(at, -6, FACE + 3, d + 2),
            offset(at, -9, FACE, d + 9),
            [at[0] - 8, 2, 50],
        ],
    )
