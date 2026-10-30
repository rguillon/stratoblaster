"""P08-R10, 2-2: the Fjord Lynx's parts (its two paw cannons and its radar mast) Logical pixels,
nose +Z, Y up (towards the camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.world_2.fjord_lynx import FJORD_LYNX  # noqa: E402
from game.config.record import record  # noqa: E402
from game.view.bosses.mini_boss_greebles import hazard  # noqa: E402
from game.view.bosses.mini_boss_mechanism import GEAR  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    SHADE,
    WHITE,
    H,
    offset,
    turret,
)
from game.view.bosses.world_2.fjord_lynx_frost import (  # noqa: E402
    RIME,
    icicles,
    snow_cap,
    spread,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    gland,
    sinew,
)
from render.geometry.solids import Placement  # noqa: E402

# The lynx's neon: cyan, and white for its secondary lights.
CYAN = BOSS_LOOK.neon["fjord-lynx"]
if CYAN == None:  # noqa: E711
    CYAN = [0.55, 0.95, 1.0]
WHITE_NEON = [0.9, 0.95, 1.0]

# A paw seen from above, around its centre: a broad pad, wider at the toes.
PAD = [
    [0.0, 12.0],
    [7.0, 10.0],
    [10.0, 3.0],
    [9.0, -6.0],
    [5.0, -10.0],
    [-5.0, -10.0],
    [-9.0, -6.0],
    [-10.0, 3.0],
    [-7.0, 10.0],
]
# One toe claw, its root on the pad's front edge, pointing to the nose.
CLAW = [
    [-1.6, 0.0],
    [1.6, 0.0],
    [0.4, 5.0],
    [-0.4, 5.4],
]
# Height of the pad's top, where the paw cannon's turret stands.
PAD_TOP = 3.5


def _mount_octagon() -> list[OutlinePoint]:
    """The radar mast's mount: an octagon of radius 7 around its centre."""
    points: list[OutlinePoint] = []
    for k in range(8):
        a = (2 * math.pi * (k + 0.5)) / 8
        points.append([math.sin(a) * 7, math.cos(a) * 7])
    return points


# The radar mast's mount (an octagon, around the part's centre).
MOUNT = _mount_octagon()
# The radar mast's height, and the scanner bar's turn on it.
MAST_HEIGHT = 15
SCANNER_YAW = 0.45


def _sign(x: float) -> float:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def at2(outline: Sequence[OutlinePoint], at: Vec3) -> list[OutlinePoint]:
    """`outline` moved to `[x, z]`."""
    x = at[0]
    z = at[2]
    return [[q[0] + x, q[1] + z] for q in outline]


def paw(p: EnemyParts, at: Vec3) -> None:
    """A paw (P08-R10): an armoured pad with three toe claws, frosted on top, its cannon on a
    turret (`paw_turret`); a ram from the foreleg works it."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    s = _sign(at[0]) or 1
    # P16-R05: a fleshy paw, bone claws, a metal armour plate where the cannon is grafted.
    flesh.bevel_slab(
        at2(PAD, at),
        [-2.5, 0.0, PAD_TOP - 1],
        [1.2, 1.6],
        ICE_FLESH.sinew,
        None,
        ICE_FLESH.rime,
    )
    hull.bevel_slab(
        at2(PAD[2:7], offset(at, 0, 0, 0)),
        [PAD_TOP - 1.2, PAD_TOP - 0.6, PAD_TOP],
        [0.0, 0.6],
        H.panel,
    )
    for dx in [-5.0, 0.0, 5.0]:
        flesh.bevel_slab(
            CLAW,
            [-1.5, -0.5, 1.2],
            [0.2, 0.4],
            ICE_FLESH.bone,
            Placement(offset(at, dx, 0, 11.5 if dx == 0 else 9.5), -dx * 0.05),
        )
    snow_cap(flesh, at2(PAD[3:7], offset(at, 0, 0, -1)), PAD_TOP)
    neon.box([1, 0.5, 9], CYAN, Placement(offset(at, s * 9, 1.4, -1), s * 0.15))
    neon.box([5, 0.5, 0.8], WHITE_NEON, Placement(offset(at, 0, PAD_TOP - 0.2, -9.6)))
    sinew(flesh, offset(at, -s * 8, 1.5, -12), offset(at, -s * 5, 2, -6), 1.4)
    gland(p, offset(at, s * 5, 1.5, -7), 0.9, CYAN)
    icicles(flesh, spread(offset(at, s * 9.5, 0, -6), offset(at, s * 9.5, 0, 3), 3), 3.5)


def paw_turret(p: EnemyParts, at: Vec3) -> None:
    """A paw's twin-barrelled cannon, on its turret."""
    turret(
        p,
        offset(at, 0, PAD_TOP, 0),
        record(
            {
                "radius": 8,
                "barrels": 2,
                "gap": 3.6,
                "bore": 1.2,
                "length": 6,
                "neon": CYAN,
                "hatch": -_sign(at[0]),
            }
        ),
    )


def chin_turret(p: EnemyParts, at: Vec3) -> None:
    """The chin cannon (the core's gun), turning on the deck in front of the head."""
    turret(
        p,
        offset(at, 0, 5, 0),
        record({"radius": 6, "barrels": 1, "gap": 0, "bore": 1.4, "length": 6, "neon": CYAN}),
    )


def radar_mast(p: EnemyParts, at: Vec3) -> None:
    """The radar mast (P08-R10): a mount on the sponson, a tapered mast, a scanner bar with a
    dish and white lights at its ends; while it stands, the guns aim at the player."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    # P16-R05: a metal mast grafted in a swollen mound of flesh, crystals around it.
    p.flesh.bevel_slab(
        at2(MOUNT, at),
        [-1.0, 0.0, 2.5],
        [0.5, 1.0],
        ICE_FLESH.purple,
        None,
        ICE_FLESH.rime,
    )
    crystals(p.flesh, offset(at, 4, 2, 3), 3)
    hazard(hull, offset(at, 0, 2.5, -5), [6, 1.6], 4, 0)
    hull.cylinder(2, MAST_HEIGHT, 4, H.panel, Placement(offset(at, 0, 2.5, 0), 0.3), 0.9)
    for h in [6, 10]:
        hull.cylinder(2.2 - h * 0.08, 0.8, 6, GEAR, Placement(offset(at, 0, 2.5 + h, 0)))
    top = offset(at, 0, 2.5 + MAST_HEIGHT, 0)
    hull.box([14, 1.4, 2.4], H.base, Placement(top, SCANNER_YAW), RIME)
    hull.lathe(
        [[0.4, 0], [4.5, 1.6], [3.8, 2.2], [0, 0.8]],
        8,
        SHADE.edge,
        Placement(offset(top, 0, 1.4, 0), SCANNER_YAW, -0.6),
    )
    for k in [-1, 1]:
        end = offset(
            top,
            k * 6.6 * math.cos(SCANNER_YAW),
            0.6,
            -k * 6.6 * math.sin(SCANNER_YAW),
        )
        neon.box([1.2, 1, 1.2], WHITE_NEON, Placement(end))
    charge.box([1.6, 1.6, 1.6], WHITE, Placement(offset(top, 0, 4, 0)))
    neon.ring(7.2, 0.6, 8, CYAN, Placement(offset(at, 0, 0.6, 0), math.pi / 8))
    icicles(hull, spread(offset(top, -5, 0, 2), offset(top, 5, 0, -2), 4), 3)


def paw_centre(side: float) -> Vec3:
    """The left paw's centre in model space (for the forelegs drawn on the core)."""
    spec = FJORD_LYNX.stats.parts[0]
    x = -30 if spec == None else spec.x  # noqa: E711
    y = -26 if spec == None else spec.y  # noqa: E711
    return [side * -x, 0.0, -y]
