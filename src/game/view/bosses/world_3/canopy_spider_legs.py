"""P09-R09, 3-2: the Canopy Spider's legs: an upper leg on each hip and a lower leg on each knee
(moving limbs, D-061), stepping in turn, and the gun pods at their feet (its parts). Ported from
`view/bosses/world-3/canopy-spider-legs.ts`. Logical pixels, nose +Z, Y up (towards the camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.world_3.canopy_spider import (
    LEG_GUN_REACH,
    LEG_HEIGHT,
    LEG_REST,
    LEGS,
    end_of,
    side_of,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import (
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import F, gland, sign_of, table
from game.view.bosses.world_3.toucan_jungle import moss, sagging, segment, vine
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The Spider's red neon (its eyes, the lines along its legs).
SPIDER_RED = BOSS_LOOK.neon["canopy-spider"]
QUARTER = math.pi / 2


def leg_points(leg: str) -> list[Vec3]:
    """The model-space points of `leg` at rest: its hip, knee and foot, at their heights."""
    s = side_of(leg)
    rest = LEG_REST[end_of(leg)]
    hip = [s * rest[0][0], rest[0][1]]
    knee = [s * rest[1][0], rest[1][1]]
    foot = [s * rest[2][0], rest[2][1]]
    return [
        boss_point(hip[0], hip[1], LEG_HEIGHT.hip),
        boss_point(knee[0], knee[1], LEG_HEIGHT.knee),
        boss_point(foot[0], foot[1], LEG_HEIGHT.foot),
    ]


def knee_joint(p: EnemyParts, knee: Vec3) -> None:
    """A knee: a faceted ball of armour, a red light on top."""
    p.hull.lathe(
        [[0, -3.6], [3.4, -2], [3.8, 0.6], [2.6, 3], [0, 3.8]],
        7,
        H.panel,
        Placement(knee),
    )
    p.neon.box([1.2, 0.6, 1.2], SPIDER_RED, Placement(offset(knee, 0, 3.6, 0)))


def upper_leg(leg: str) -> Any:
    """`leg`'s upper leg, on its hip: an armoured strut rising to the knee, a red line along it."""

    def draw(p: EnemyParts) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        points = leg_points(leg)
        hip = points[0]
        knee = points[1]
        # P16-R06: a jointed leg of purple chitin over sinew, a metal knee joint grafted on.
        segment(flesh, [hip, knee], [3.4, 2.6], F.purple, 6)
        segment(
            flesh,
            [offset(hip, 0, 2.6, 0), offset(knee, 0, 2.2, 0)],
            [1.6, 1.2],
            F.sinew,
            4,
        )
        segment(
            neon,
            [offset(hip, 0, 3.7, 0), offset(knee, 0, 3.2, 0)],
            [0.45, 0.4],
            SPIDER_RED,
            4,
        )
        hull.cylinder(4.2, 3, 7, H.dark, Placement(offset(hip, 0, -1.5, 0)), 3.6)
        knee_joint(p, knee)
        moss(hull, offset(knee, 0, 3.4, 0), 2.6, hip[0] + hip[2])

    return draw


def lower_leg(leg: str) -> Any:
    """`leg`'s lower leg, on its knee: a tapering shin dropping to its foot, a vine around it."""

    def draw(p: EnemyParts) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        points = leg_points(leg)
        knee = points[1]
        foot = points[2]
        ankle = offset(foot, 0, 5, 0)
        segment(flesh, [knee, ankle], [2.6, 1.7], F.purple, 6)
        segment(
            neon,
            [offset(knee, 0, 2.2, 0), offset(ankle, 0, 1.4, 0)],
            [0.4, 0.3],
            SPIDER_RED,
            4,
        )
        # Spines along its back.
        for t in [0.3, 0.6]:
            at: Vec3 = [
                knee[0] + (ankle[0] - knee[0]) * t,
                knee[1] + (ankle[1] - knee[1]) * t + 1.6,
                knee[2] + (ankle[2] - knee[2]) * t,
            ]
            flesh.cylinder(0.7, 2.6, 4, F.bone, Placement(at), 0)
        vine(
            hull,
            sagging(offset(knee, 0, -1, 0), offset(ankle, 0, -1.4, 0), 4, 2.4),
            0.4,
        )

    return draw


def leg_limbs() -> dict[str, Any]:
    """The limbs of the four legs: an upper leg on each hip and a lower leg on each knee."""
    limbs: dict[str, Any] = {}
    for leg in LEGS:
        limbs["hip-" + leg] = {"draw": upper_leg(leg)}
        limbs["knee-" + leg] = {"draw": lower_leg(leg)}
    return limbs


# A gun pod's armoured foot (a lathe profile around its centre).
FOOT = table([[4, 0], [6.4, 1.6], [6, 4.4], [3.6, 6.6], [0, 7.2]])


def leg_gun_pod(p: EnemyParts, at: Vec3) -> None:
    """A leg's gun pod at its foot `at` (P09-R09): an armoured foot gripping the canopy with three
    claws, a red ring around it, and a gun pointing forward that fires aimed spreads."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    s = sign_of(at[0])
    foot = offset(at, 0, LEG_HEIGHT.foot - 3, 0)
    # P16-R06: a swollen flesh foot gripping with bone claws, its gun a grafted metal pod.
    p.flesh.lathe(FOOT, 7, F.crimson, Placement(foot))
    gland(p, offset(foot, 0, 5.2, 0), 2, SPIDER_RED)
    neon.ring(6.5, 0.7, 7, SPIDER_RED, Placement(offset(foot, 0, 1.8, 0)))
    for yaw in [s * 1.2, s * 2.2, math.pi]:
        out = offset(foot, math.sin(yaw) * 7, 0, math.cos(yaw) * 7)
        p.flesh.box([1.6, 1.4, 5], F.bone, Placement(out, yaw, 0.35))
    tip: Vec3 = [at[0], LEG_HEIGHT.foot, at[2] + LEG_GUN_REACH]
    hull.box([4.4, 3.4, 5], H.base, Placement(offset(tip, 0, -1.7, -9.5)), H.panel)
    hull.cylinder(1.3, 6.4, 6, H.dark, Placement(offset(tip, 0, 0, -7), 0, QUARTER))
    charge.cylinder(1.35, 0.6, 6, WHITE, Placement(offset(tip, 0, 0, -0.6), 0, QUARTER))
    muzzle(tip)
