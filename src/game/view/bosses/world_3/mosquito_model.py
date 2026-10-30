"""P09-R09, 3-4: the Mosquito. Logical pixels,
nose +Z, Y up (towards the camera). A thin bio-drone: a small armoured thorax, a big-eyed head, a
long segmented abdomen behind, six thin legs hanging under it, moss grown over its back."""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_3.mosquito import MOSQUITO, MOSQUITO_MANDIBLES, MOSQUITO_SAC
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import rod
from game.view.bosses.mini_boss_greebles import (
    lamps,
    seam,
)
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
)
from game.view.bosses.world_3.jungle_flesh import F, sinew, table, vein_to
from game.view.bosses.world_3.mosquito_parts import (
    MOSQUITO_PINK,
    MOSS,
    moss,
    needle,
    proboscis,
    wing,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import ROUND_SECTION, tendril
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The thorax along the centre line (loft stations: z, half width, bottom, top).
THORAX = table(
    [
        [-9, 5, -2, 6],
        [0, 9, -3, 9],
        [10, 8, -3, 8],
        [16, 5, -1, 5],
    ]
)
# The abdomen, tail to waist: long and segmented.
ABDOMEN = table(
    [
        [-44, 1.2, 1, 2.6],
        [-38, 4.5, -1, 5.5],
        [-26, 6.5, -2, 7.5],
        [-14, 6.5, -2, 7.5],
        [-8, 4, -1, 5],
    ]
)
# Where the abdomen's segments meet: a pink band across its back at each.
SEGMENTS = table(
    [
        [-20, 6.4, 7.8],
        [-27, 6.2, 7.6],
        [-34, 5, 6.6],
    ]
)
# The head: a rounded capsule (a lathe profile along its axis, Y up).
HEAD = table([[0, -4.5], [4, -3.8], [6, -1], [5.6, 2], [3.6, 4.4], [0, 5.2]])
HEAD_AT = [0, 2.5, 21]
# A compound eye: a low neon dome, turned to face its side.
EYE = table([[3.2, 0], [2.7, 1.6], [1.4, 2.5], [0, 2.8]])
# The legs, front to back (left side, +X): hip, knee and foot.
LEGS = table(
    [
        [[6, 0, 9], [19, 5, 15], [25, -7, 22]],
        [[7, 0, 3], [22, 5, 2], [29, -8, 0]],
        [[6, 0, -4], [20, 5, -12], [26, -8, -20]],
    ]
)
# The blood sac on its back (a lathe dome), lighting up as its next ring charges.
SAC = table([[3.6, 0], [3.1, 1.5], [1.6, 2.3], [0, 2.5]])


def draw_body(p: EnemyParts) -> None:
    """The thorax and the segmented abdomen, pink bands between the segments, moss on its back."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a living insect: a purple flesh thorax, a swollen, blood-filled abdomen ringed by
    # grafted metal bands, a vein pulsing down its back.
    flesh.loft(ROUND_SECTION, THORAX, F.purple)
    flesh.loft(ROUND_SECTION, ABDOMEN, F.crimson)
    vein_to(p, [[0, 6.4, 12], [0, 4.2, -40]], [0, 2, 0], MOSQUITO_PINK, 1)
    for seg in SEGMENTS:
        z = seg[0]
        w = seg[1]
        y = seg[2]
        neon.box([w * 1.6, 0.4, 0.8], MOSQUITO_PINK, Placement([0, y, z]))
        hull.box([w * 2.1, 1, 1.4], H.dark, Placement([0, y - 2.4, z]))
    seam(hull, [0, 14], [0, -6], [8.6, 1.2, 0.6], SHADE["edge"])
    moss(
        hull,
        [[3.5, 8.4, 4], [-4, 8.2, -3], [2, 7.2, -24], [-2.5, 6.6, -33]],
    )
    # A strand of vine trailing from its side.
    rod(hull, [-6, 1, -22], [-10, -6, -30], 0.5, MOSS)
    reactor_sac(p, table([0, 1.8, -44.4]), 1.6, MOSQUITO_PINK, F.purple, None)
    for s in SIDES:
        p.reactor([s * 5, 2, -9.2], 1.6)


def draw_head(p: EnemyParts) -> None:
    """The head: big pink compound eyes and the mandible guns under them (the core's bursts)."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    flesh.lathe(HEAD, 7, F.purple, Placement(HEAD_AT, 0, QUARTER))
    for s in SIDES:
        neon.lathe(EYE, 6, MOSQUITO_PINK, Placement([s * 4.6, 3.4, 22.5], 0, 0, -s * QUARTER))
        # P16-R05: feathery antennae of sinew, tipped with a lit gland.
        sinew(
            p,
            [[s * 2, 7, 22], [s * 6, 12, 15]],
            [s * 0.6, 1, 0],
            0.45,
        )
        lamps(neon, [[s * 6, 12, 15]], 0.9, MOSQUITO_PINK)
    for m in MOSQUITO_MANDIBLES:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.box([2.6, 2.6, 4], H.panel, Placement([x, y - 1.4, z - 6]), SHADE["edge"])
        hull.cylinder(0.9, 5.4, 6, H.dark, Placement([x, y, z - 6], 0, QUARTER))
        charge.cylinder(0.95, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)


def draw_legs(p: EnemyParts) -> None:
    """Six thin legs hanging under the thorax, bent at the knee."""
    for s in SIDES:
        for leg in LEGS:
            hip = leg[0]
            knee = leg[1]
            foot = leg[2]
            hip_s = [s * hip[0], hip[1], hip[2]]
            knee_s = [s * knee[0], knee[1], knee[2]]
            foot_s = [s * foot[0], foot[1], foot[2]]
            # P16-R05: thin legs of sinew, a metal knee joint grafted where they bend.
            tendril(p.flesh, [hip_s, knee_s], [0.8, 0.6], 4, F.sinew)
            tendril(p.flesh, [knee_s, foot_s], [0.55, 0.15], 3, F.bone)
            p.hull.box([1.4, 1.4, 1.4], H.panel, Placement(knee_s))


def draw_sac(p: EnemyParts) -> None:
    """The blood sac on its back, where its last-stage rings leave from."""
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(MOSQUITO_SAC) == 0:
        return
    top = boss_point(MOSQUITO_SAC[0][0], MOSQUITO_SAC[0][1], MOSQUITO_SAC[0][2])
    x = top[0]
    y = top[1]
    z = top[2]
    # P16-R05: the blood sac swelling out of the abdomen's flesh.
    flesh.cylinder(4.4, 1.6, 7, F.wound, Placement([x, y - 4.2, z]))
    neon.ring(4.5, 0.4, 8, MOSQUITO_PINK, Placement([x, y - 3, z]))
    charge.lathe(SAC, 8, WHITE, Placement([x, y - 2.5, z]))
    muzzle(top, "ring")


def mosquito_core(p: EnemyParts) -> None:
    """The core of the Mosquito: its body, head, legs and sac."""
    draw_body(p)
    draw_head(p)
    draw_legs(p)
    draw_sac(p)


def build_mosquito(scene: Any) -> Any:
    """P09-R09: the Mosquito, a thin, fast bio-drone with pink neon: long buzzing wings with a fan
    pod under each, a big-eyed head and a needle-like proboscis that aims its laser."""
    parts: dict[str, Any] = {"wing-left": wing, "wing-right": wing, "proboscis": proboscis}
    turrets: dict[str, Any] = {"proboscis": needle}
    return build_boss_model(
        MOSQUITO,
        scene,
        MOSQUITO_PINK,
        {"core": mosquito_core, "parts": parts, "turrets": turrets},
    )
