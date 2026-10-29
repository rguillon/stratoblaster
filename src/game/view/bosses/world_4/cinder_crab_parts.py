"""P10-R11, 4-1: the Cinder Crab's arms (on their shoulders) and outer fingers (on their wrists),
moving limbs (D-061), its claws and its back mortar (its parts). Ported from
`bosses/world-4/cinder-crab-parts.ts`. Logical pixels, nose +Z, Y up; the left claw (the screen's
left, -X on the playfield) is drawn at +X.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_4.cinder_crab import (  # noqa: E402
    CRAB_ARM,
    CRAB_MORTAR,
    CRAB_PALM_GUN,
    CRAB_SWING,
)
from game.config.record import record  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.mini_boss_shapes import SHADE, H, offset  # noqa: E402
from game.view.bosses.world_4.black_sands_kit import (  # noqa: E402
    FORGE,
    barrel_to,
    blot,
    molten_seam,
    soot,
    strut,
)
from game.view.bosses.world_4.living_forge import SKIN, glands  # noqa: E402
from game.view.enemies.enemy_shapes import flip_x  # noqa: E402
from render.geometry.outline import hypot3  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
type OutlinePoint = list[float]
__pragma__("noskip")


def _sign(v: float) -> float:
    """`Math.sign`."""
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def _neon_or(kind: str, fallback: Rgb) -> Rgb:
    """`BOSS_LOOK.neon[kind] ?? fallback`."""
    colour: Rgb = BOSS_LOOK.neon[kind]
    if colour == None:  # noqa: E711
        return fallback
    return colour


# The Cinder Crab's orange neon (P10-R11).
CRAB_ORANGE = _neon_or("cinder-crab", [1, 0.45, 0.05])

# The claw's palm seen from above, around the claw's centre (x across, z along).
PALM = [
    [-6.0, -8.0],
    [6.0, -8.0],
    [7.5, -2.0],
    [6.5, 6.0],
    [-6.5, 6.0],
    [-7.5, -2.0],
]
# The palm's heights: its bottom, its waist and its top.
PALM_Y = [0.0, 3.0, 7.5]
# A left claw's fingers seen from above (x across, z along), from their roots: the fixed one on the
# inner side (towards -X) and the moving one on the outer side, each curving in to its tip, as they
# are shut.
FIXED_FINGER = [
    [-2.6, 0.0],
    [2.4, 0.0],
    [2.0, 9.0],
    [0.6, 16.0],
    [-1.0, 17.0],
    [-2.8, 10.0],
]
MOVING_FINGER = [
    [-2.4, 0.0],
    [2.8, 0.0],
    [3.0, 10.0],
    [1.0, 17.5],
    [-0.6, 18.0],
    [-2.0, 9.0],
]
# The fingers' heights, and how far from the claw's middle line they stand.
FINGER_Y = [0.5, 2.5, 5.5]
FINGER_OUT = 4.6


def side_at(at: list[float]) -> float:
    """The side of a claw drawn at `at`: +1 for the left one (at +X), -1 for the right one."""
    s = _sign(at[0])
    if s == 0:
        return 1
    return s


def _flipped(outline: Any) -> Any:
    """`flipX` of an outline (enemy_shapes types its points as tuples)."""
    mirrored: Any = flip_x(outline)
    return mirrored


def _sided(outline: Any, s: float) -> Any:
    """`outline` for the claw on side `s` (+1 the left one), mirrored for the right one."""
    if s > 0:
        return outline
    return _flipped(outline)


def claw(p: Any, at: Vec3) -> None:
    """The claw on side `s` (P10-R11), around its centre `at`: an armoured palm with a molten seam
    across it, an orange light along its outer side, the fixed finger on its inner side and the palm
    gun between the fingers."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    s = side_at(at)
    # P16-R05: a swollen flesh palm, bone pincers, a molten gland.
    flesh.bevel_slab(PALM, PALM_Y, [1, 1.6], SKIN.base, Placement(at), SKIN.panel)
    glands(p, [offset(at, -s * 2.5, PALM_Y[2] - 0.4, 3)], 1.6, FORGE["molten"])
    fixed = offset(at, -s * FINGER_OUT, 0, 5)
    flesh.bevel_slab(_sided(FIXED_FINGER, s), FINGER_Y, [0.6, 0.9], SKIN.bone, Placement(fixed))
    for dz in [5, 10]:
        hull.box([1.4, 1.6, 1.2], SHADE["edge"], Placement(offset(fixed, s * 2.2, 1.5, dz)))
    neon.box([0.8, 0.8, 11], CRAB_ORANGE, Placement(offset(at, s * 7.3, 2.6, -1.5), -s * 0.08))
    molten_seam(
        neon,
        [
            [at[0] - 5, at[2] - 3],
            [at[0] - 1, at[2] - 1.5],
            [at[0] + 2, at[2] - 4],
            [at[0] + 5, at[2] - 2],
        ],
        PALM_Y[2],
    )
    soot(hull, blot([at[0] + s * 2, at[2] + 2], 2.6, 1, s), PALM_Y[2])
    guns = CRAB_PALM_GUN if s > 0 else mirror(CRAB_PALM_GUN)
    for tip in guns:
        barrel_to(p, tip, [1.6, 9])


# Where a claw's arm bends and meets its palm (x across, height, z along), the left one.
ELBOW_OUT = 30
ELBOW_HEIGHT = 7
ELBOW_Z = 22


def arm(s: float) -> Any:
    """The arm on side `s`: a shoulder ball, an armoured upper arm out to the elbow, a forearm."""

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        flesh = p.flesh
        shoulder_at = CRAB_ARM.shoulder
        claw_at = CRAB_ARM.claw
        shoulder = boss_point(s * shoulder_at[0], shoulder_at[1], 5)
        elbow = [s * ELBOW_OUT, ELBOW_HEIGHT, ELBOW_Z]
        wrist = offset(boss_point(s * claw_at[0], claw_at[1], 4), -s * 1, 0, -6)
        flesh.lathe(
            [
                [0, -1],
                [4, 0.5],
                [4, 3],
                [0, 4.5],
            ],
            7,
            SKIN.panel,
            Placement(offset(shoulder, 0, -2, 0)),
        )
        strut(flesh, [shoulder, elbow], [3.2, 2.8], SKIN.base)
        strut(flesh, [elbow, wrist], [2.8, 2.4], SKIN.panel)
        hull.lathe(
            [
                [0, -3],
                [3.4, -1.5],
                [3.4, 1.5],
                [0, 3.2],
            ],
            6,
            H.dark,
            Placement(elbow),
        )
        strut(
            neon,
            [offset(shoulder, 0, 3, 0), offset(elbow, 0, 2.8, 0)],
            [0.45, 0.45],
            CRAB_ORANGE,
            4,
        )
        strut(
            neon,
            [offset(elbow, 0, 2.5, 0), offset(wrist, 0, 2.4, 0)],
            [0.4, 0.4],
            FORGE["molten"],
            4,
        )

    return draw


def turn(p: Vec3, yaw: float) -> Vec3:
    """`[x, y, z]` turned by `yaw` around +Y (as `SolidBuilder` places a yawed solid)."""
    c = math.cos(yaw)
    k = math.sin(yaw)
    return [p[0] * c + p[2] * k, p[1], -p[0] * k + p[2] * c]


def finger(s: float) -> Any:
    """The moving finger on side `s`, on its wrist, drawn half open (as at rest): it swings from
    shut to wide open with its joint (D-061), a hot glow along its inner edge."""

    def draw(p: Any) -> None:
        hull = p.hull
        neon = p.neon
        flesh = p.flesh
        wrist_at = CRAB_ARM.wrist
        pivot = boss_point(s * wrist_at[0], wrist_at[1], 0)
        yaw = (s * CRAB_SWING.fingerDeg * math.pi) / 180
        root = turn([s * FINGER_OUT, 0, 1], yaw)
        at = offset(pivot, root[0], 0, root[2])
        flesh.bevel_slab(
            _sided(MOVING_FINGER, s), FINGER_Y, [0.6, 0.9], SKIN.bone, Placement(at, yaw)
        )
        for dz in [5, 10, 14]:
            tooth = turn([-s * 2.2, 1.5, dz], yaw)
            hull.box(
                [1.4, 1.6, 1.2],
                SHADE["edge"],
                Placement(offset(at, tooth[0], 1.5, tooth[2]), yaw),
            )
        glow = turn([-s * 1.4, 0, 8], yaw)
        neon.box(
            [0.6, 0.6, 9],
            FORGE["molten"],
            Placement(offset(at, glow[0], FINGER_Y[2] - 0.3, glow[2]), yaw),
        )

    return draw


# The arms and moving fingers (D-061): each drawn on its joint, they go and flash with their claw.
CRAB_LIMBS = {
    "arm-left": record({"draw": arm(1), "part": "claw-left"}),
    "arm-right": record({"draw": arm(-1), "part": "claw-right"}),
    "finger-left": record({"draw": finger(1), "part": "claw-left"}),
    "finger-right": record({"draw": finger(-1), "part": "claw-right"}),
}

# The mortar's turntable (a lathe profile, bottom to top), and the barrel's bore.
TURNTABLE = [
    [8.5, 0.0],
    [8.5, 1.8],
    [6.5, 4.2],
    [0.0, 4.8],
]
BORE = 3.2


def mortar(p: Any, at: Vec3, base: float) -> None:
    """The back mortar (P10-R11) around its centre `at`, standing on the carapace at height `base`:
    a squat turntable with an orange ring, a fat barrel leaning forward over the carapace on its
    trunnions, its mouth glowing as it loads."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(CRAB_MORTAR) == 0:
        return
    mouth = CRAB_MORTAR[0]
    tip = boss_point(mouth[0], mouth[1], mouth[2])
    foot = offset(at, 0, base, 0)
    hull.lathe(TURNTABLE, 8, H.panel, Placement(foot, math.pi / 8))
    neon.ring(8.6, 0.6, 8, CRAB_ORANGE, Placement(offset(foot, 0, 1, 0), math.pi / 8))
    pivot = offset(foot, 0, 4.2, 2)
    dx = tip[0] - pivot[0]
    dy = tip[1] - pivot[1]
    dz = tip[2] - pivot[2]
    length = hypot3(dx, dy, dz)

    def along(t: float) -> Vec3:
        return offset(pivot, (dx * t) / length, (dy * t) / length, (dz * t) / length)

    light = BORE * 0.7
    strut(hull, [along(-3), along(length - light)], [BORE + 0.6, BORE], H.dark, 8)
    strut(
        hull,
        [along(length - light - 3), along(length - light)],
        [BORE + 0.9, BORE + 0.9],
        H.panel,
        8,
    )
    strut(charge, [along(length - light), tip], [BORE * 0.85, BORE * 0.85], [1, 1, 1], 8)
    muzzle(tip)
    for x in [-1, 1]:
        hull.box([2.6, 4, 4], H.dark, Placement(offset(pivot, x * 4.4, -2, 0)))
