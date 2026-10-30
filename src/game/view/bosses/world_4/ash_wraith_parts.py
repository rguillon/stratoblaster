"""P10-R11, 4-2: the Ash Wraith's parts: its two shroud pods (ducted fans under ragged shrouds)
and its eye cannon (a mount on the nose, the eye itself on a turret). Ported from
`bosses/world-4/ash-wraith-parts.ts`. Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_4.ash_wraith import WRAITH_EYE_LENS, WRAITH_POD_GUNS  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset  # noqa: E402
from game.view.bosses.world_4.ash_plains_soot import ASH_THIN, EMBER, ash_drift  # noqa: E402
from game.view.bosses.world_4.living_forge import SKIN, glands  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
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


# The Wraith's pale cyan neon (P10-R11).
WRAITH_CYAN = _neon_or("ash-wraith", [0.55, 0.95, 1])

# A pod's duct around its fan: an open lathe, wider at its lip (around the pod's centre).
DUCT = [
    [9.4, -1.5],
    [11.0, -0.5],
    [11.2, 3.4],
    [10.0, 5.0],
]
# A torn strip of the shroud hanging off a duct (seen from above, from its root outwards).
TATTER = [
    [-1.6, 0.0],
    [1.6, 0.0],
    [1.0, 4.6],
    [0.2, 3.4],
    [-0.8, 5.4],
]


def _tatters(flesh: Any, at: Vec3, s: float) -> None:
    """Torn strips of the shroud around a duct at `at`, out towards the back and the side `s`."""
    yaws = [math.pi * 0.75, math.pi, math.pi * 1.2, s * math.pi * 0.55]
    for k in range(len(yaws)):
        yaw = yaws[k]
        root = offset(at, math.sin(yaw) * 10.6, 3.6 - (k % 2) * 0.8, math.cos(yaw) * 10.6)
        colour = SKIN.dark if k % 2 == 0 else SKIN.base
        flesh.slab(TATTER, [0, 0.4], colour, Placement(root, yaw, -0.25))


def shroud_pod(p: Any, at: Vec3) -> None:
    """A shroud pod around its centre `at` (P10-R11): a ducted fan, its lip ringed with pale cyan
    neon, torn grey shroud strips trailing off it, ash on its lip, a gun housing under its front
    with the two barrels of its fans."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    s = _sign(at[0])
    # P16-R05: a flesh gill ringing its fan, torn membrane trailing off it.
    p.flesh.lathe(DUCT, 10, SKIN.base, Placement(at, math.pi / 10), False)
    hull.cylinder(9.4, 0.5, 10, H.dark, Placement(offset(at, 0, 0.2, 0)))
    hull.cylinder(2.4, 3, 6, H.base, Placement(offset(at, 0, 0.6, 0)))
    p.rotor(offset(at, 0, 3, 0), 8.4)
    neon.ring(11.3, 0.7, 10, WRAITH_CYAN, Placement(offset(at, 0, 3.9, 0), math.pi / 10))
    _tatters(p.flesh, at, s)
    glands(p, [offset(at, -s * 9, 3, -4)], 1.3, WRAITH_CYAN)
    ash_drift(hull, offset(at, s * 8.6, 5, -5), 2.6, at[0])
    hull.box([9, 3, 6], H.base, Placement(offset(at, 0, 0.3, 9)), H.panel)
    # The right pod (screen right) is on the model's -X side.
    guns = WRAITH_POD_GUNS if s < 0 else mirror(WRAITH_POD_GUNS)
    for m in guns:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(1.1, 5.6, 6, H.dark, Placement([x, y, z - 6.2], 0, QUARTER))
        charge.cylinder(1.15, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)


# The eye's mount on the nose: an armoured collar (a lathe profile around its pivot).
COLLAR = [
    [8.6, 0.0],
    [9.4, 1.6],
    [8.0, 3.2],
    [6.4, 3.4],
]


def eye_mount(p: Any, at: Vec3) -> None:
    """The eye cannon's mount around its pivot `at` (P10-R11): a collar on the nose, a cyan ring."""
    p.flesh.lathe(COLLAR, 9, SKIN.panel, Placement(at, math.pi / 9))
    p.neon.ring(9.5, 0.5, 9, WRAITH_CYAN, Placement(offset(at, 0, 1.2, 0), math.pi / 9))
    p.hull.cylinder(6.2, 3.3, 9, H.dark, Placement(at))
    for yaw in [math.pi * 0.8, math.pi * 1.2]:
        p.hull.box(
            [1.2, 1.2, 5],
            SHADE["edge"],
            Placement(offset(at, math.sin(yaw) * 8, 2.6, math.cos(yaw) * 8), yaw),
        )


# The eye's ball (a lathe profile around its pivot): a faceted, flattened sphere.
BALL = [
    [0.0, 3.0],
    [4.6, 3.6],
    [6.0, 5.6],
    [5.0, 7.8],
    [2.6, 9.0],
    [0.0, 9.2],
]


def eye_turret(p: Any, at: Vec3) -> None:
    """The eye cannon (P10-R11), turning on its mount: a dark armoured ball, a heavy lid over it,
    the lens barrel reaching forward, its pale iris and lens lit as the laser charges."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    # `const [m] = WRAITH_EYE_LENS; const tip = m ? bossPoint(...m) : at;`
    if len(WRAITH_EYE_LENS) > 0:
        m = WRAITH_EYE_LENS[0]
        tip = boss_point(m[0], m[1], m[2])
    else:
        tip = at
    # P16-R05: a living eyeball under a metal lid.
    p.flesh.lathe(BALL, 9, SKIN.bone, Placement(at))
    hull.box([7, 1.2, 5], H.dark, Placement(offset(at, 0, 8.2, -1.5), 0, -0.18), ASH_THIN)
    hull.cylinder(2.6, 6, 8, H.dark, Placement([tip[0], tip[1], at[2] + 3.2], 0, QUARTER), 2.2)
    hull.cylinder(
        1.8,
        tip[2] - at[2] - 9.8,
        8,
        H.panel,
        Placement([tip[0], tip[1], at[2] + 9.2], 0, QUARTER),
        1.6,
    )
    neon.ring(2.9, 0.6, 8, WRAITH_CYAN, Placement([tip[0], tip[1], at[2] + 5.6], 0, QUARTER))
    neon.ring(2.1, 0.4, 8, EMBER, Placement([tip[0], tip[1], tip[2] - 2.6], 0, QUARTER))
    charge.cylinder(1.5, 0.6, 8, WHITE, Placement(offset(tip, 0, 0, -0.6), 0, QUARTER))
    muzzle(tip, "laser")
