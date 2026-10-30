"""P07-R05, P16-R05, 1-5: the Sentinel, ported from `bosses/sentinel-model.ts`: a twin-bodied city
hunter, a blue body and a red one joined by a membrane through its thorax. Logical pixels, nose +Z,
Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.mini_bosses import SENTINEL  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import lamps, mast  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    WHITE,
    offset,
    radius_of,
    scaled,
    socket,
    turret,
)
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    gland,
    graft,
    growth,
    hide,
    mantle,
    polygon,
    rib_cage,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES, flip_x  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    MembraneWing,
    SegmentedBody,
    membrane_wing,
    organ,
    segmented_body,
)
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

QUARTER = math.pi / 2
BLUE = BOSS_LOOK.neon["sentinel"]
# The police red of the Sentinel's other hull (its boss neon colour is the blue).
POLICE_RED = [1, 0.08, 0.1]
# Where the hulls run, either side of the centre line: the +X hull is blue, the -X one red.
HULL_X = 30

# The membrane joining the bodies through the thorax, and the right tail fin (mirrored).
WING = [
    [-14, 12],
    [14, 12],
    [HULL_X, 4],
    [HULL_X, -16],
    [14, -22],
    [-14, -22],
    [-HULL_X, -16],
    [-HULL_X, 4],
]
FIN = [
    [37, -13],
    [57, -29],
    [57, -34],
    [37, -31],
]
# Height of the hulls' flat backs.
BACK = 7.5
# A plate on the membrane between the thorax and a body (around its centre).
WING_PANEL = [
    [-3, -12],
    [3, -12],
    [3, -1],
    [-3, 1],
]
# A plate grafted on the red body's back (the blue body's extra plate is the same, further back).
PATCH = [
    [-34, -6],
    [-26, -7],
    [-26, 2],
    [-33, 3],
]
# A gun's sponson on the hull's outer flank, around the gun's centre.
SPONSON = [
    [-10, 9],
    [5, 11],
    [12, 5],
    [12, -6],
    [5, -11],
    [-10, -9],
]
# The drone bay around its centre: its housing, and the hatch in its top.
BAY = [
    [-9, 15],
    [9, 15],
    [15, 7],
    [15, -12],
    [-15, -12],
    [-15, 7],
]
HATCH = [
    [-7, 10],
    [7, 10],
    [10, 5],
    [10, -7],
    [-10, -7],
    [-10, 5],
]
BAY_TOP = 6


def _sign_of(x: float) -> float:
    """`Math.sign(x)`."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def _draw_hull(p: Any, x: float, color: Any) -> None:
    """A body at `x` (P16-R05): a long segmented worm along Z, a shell plated on its back, lit veins
    along its flanks in `color`, its tail fin a membrane on bone struts."""
    at = [x, 0, 0]
    hide(
        p,
        {
            "tail": -38,
            "nose": 47,
            "width": 10,
            "bottom": -4,
            "top": BACK,
            "segments": 4,
            "shell": [F.purple, F.membrane],
            "belly": F.crimson,
            "at": at,
        },
    )
    s = _sign_of(x)
    for side in SIDES:
        vein_line(p, [x + side * 9, 2.5, -24], [x + side * 9, 2.5, 30], [side, 0.5, 0], 1.1, color)
    p.neon.box([0.6, 0.3, 30], color, Placement([x, BACK + 0.2, -4]))
    fin = FIN if x > 0 else flip_x(FIN)  # type: ignore[arg-type]
    root = fin[0]
    tips = fin[1:]
    membrane_wing(
        p.flesh,
        p.flesh,
        MembraneWing(root, tips, 2, 1, 1.2),  # type: ignore[arg-type]
        [F.membrane, F.bone],
    )
    lamps(p.neon, [[s * 56, 3.2, -32]], 1.4, color)
    graft(p, polygon(4, 4, [1, 1.8]), [BACK - 0.2, BACK + 0.8], [x, 0, 31])
    barbs(p, [x, BACK + 0.5, -20], {"count": 3, "spacing": 4, "size": 2.5, "dir": [0, 1, -0.4]})


def _draw_gear(p: Any) -> None:
    """Grafts on the bodies (P16-R05): a radome and mast on the red one, a searchlight and an extra
    plate on the blue one, a whip antenna off-centre on the thorax."""
    mast(p, [-HULL_X - 3, BACK, 10], 9, POLICE_RED)
    graft(p, PATCH, [BACK, BACK + 0.8], [0, 0, 0], {"color": M.base})
    p.hull.cylinder(2.2, 2, 6, M.panel, Placement([HULL_X, BACK, 20]))
    p.hull.box([3.6, 2.4, 2], M.dark, Placement([HULL_X, BACK + 2, 20.5], 0, -0.2))
    p.charge.box([2.8, 1.6, 0.4], WHITE, Placement([HULL_X, BACK + 2.4, 21.6], 0, -0.2))
    graft(p, scaled(PATCH, 1, 2 * HULL_X, -14), [BACK, BACK + 1], [0, 0, 0])
    mast(p, [-3.5, 9.4, -20], 7, BLUE)
    for s in SIDES:
        graft(
            p,
            scaled(WING_PANEL, 1, s * 17.5, 0),
            [2.5, 3],
            [0, 0, 0],
            {"color": M.base},
        )
        vein_line(
            p,
            [s * 8, 5, 0],
            [s * 22, 2.2, -14],
            [0, 1, 0],
            0.8,
            BLUE if s > 0 else POLICE_RED,
        )


def _draw_body(p: Any) -> None:
    """The thorax with its glands, the membrane joining the bodies, both bodies, the core's guns."""
    mantle(p, WING, [-1.5, 2.5], F.membrane)
    rib_cage(p, [-14, 2], {"halfWidth": HULL_X - 6, "y": 1, "height": 3, "thickness": 0.9})
    segmented_body(
        p.flesh,
        SegmentedBody(-28, 24, 3, 11, -3, 10),
        F.crimson,
    )
    eyes(p, [0, 7, 18], {"count": 2, "size": 1.2, "spacing": 4}, BLUE)
    # The light bar on the thorax's back: a red gland and a blue one.
    gland(p, [2.4, 9, -8], 1.6, BLUE)
    gland(p, [-2.4, 9, -8], 1.6, POLICE_RED)
    p.neon.box([3.6, 0.6, 2.4], BLUE, Placement([2.4, 10.4, -12]))
    p.neon.box([3.6, 0.6, 2.4], POLICE_RED, Placement([-2.4, 10.4, -12]))
    _draw_hull(p, HULL_X, BLUE)
    _draw_hull(p, -HULL_X, POLICE_RED)
    for s in SIDES:
        # The core's fan guns, grafted in the membrane's leading edge either side of the thorax.
        p.hull.cylinder(1.8, 3, 6, M.dark, Placement([s * 15, 1, 7], 0, QUARTER))
        p.charge.cylinder(1.4, 2.5, 6, WHITE, Placement([s * 15, 1, 10], 0, QUARTER), 1)
        p.muzzle([s * 15, 1, 12.5], None)
        socket(p.hull, [s * 38, 1, 8], 7, 1)
    # The brood pouch's grafted frame on the thorax's front.
    p.hull.box([18, 2, 4], M.dark, Placement([0, 0, 23]))


def _hull_gun(p: Any, at: Vec3) -> None:
    """A hull gun (P07-R05, P16-R05): an armoured growth on the body's outer flank under its
    turret."""
    sponson = SPONSON if at[0] > 0 else flip_x(SPONSON)  # type: ignore[arg-type]
    p.flesh.bevel_slab(sponson, [-2, 0.5, 3], [0.8, 1.6], F.crimson, Placement(at), F.sinew)
    growth(
        p,
        offset(at, 0, 1, 0),
        9,
        BLUE if at[0] > 0 else POLICE_RED,
        {"flesh": F.purple, "height": 0.35},
    )


def _hull_gun_turret(p: Any, at: Vec3) -> None:
    """A hull gun's twin-barrelled turret."""
    r = radius_of(SENTINEL.stats.parts, 0, 13)
    outer = at[0] > 0
    neon = BLUE if outer else POLICE_RED
    turret(
        p,
        offset(at, 0, 4, 0),
        {
            "radius": r * 0.85,
            "barrels": 2,
            "gap": 3.6,
            "bore": 1.3,
            "length": 7,
            "neon": neon,
            "hatch": -1 if outer else 1,
        },
    )


def _drone_bay(p: Any, at: Vec3) -> None:
    """The drone bay (P07-R05, P16-R05): a swollen brood pouch at the nose, its slit lit, launch
    glands at its corners, two drones hatching from it; a grafted rim plate behind."""
    p.flesh.bevel_slab(BAY, [-3, 1, BAY_TOP - 1], [1, 3], F.crimson, Placement(at), F.purple)
    organ(p.flesh, 10, 7, F.purple, Placement(offset(at, 0, 0, 1)), 0.35)
    p.neon.box([0.5, 0.3, 16], BLUE, Placement(offset(at, 0, BAY_TOP + 0.4, 1.5)))
    for cell in scaled(HATCH, 1.12):
        p.charge.box([2, 0.8, 2], WHITE, Placement(offset(at, cell[0], BAY_TOP - 1.5, cell[1])))
    for s in SIDES:
        p.vein.box(
            [0.8, 0.5, 14],
            BLUE if s > 0 else POLICE_RED,
            Placement(offset(at, s * 13, BAY_TOP - 2.5, -2)),
        )
        # A drone hatching on each side of the slit, ready to drop.
        drone = offset(at, s * 4, BAY_TOP + 0.2, 2)
        organ(p.flesh, 1.6, 5, F.sinew, Placement(drone), 0.6)
        p.hull.box([4.4, 0.6, 1], M.panel, Placement(drone, s * 0.8))
        p.neon.box([1, 0.6, 1], BLUE if s > 0 else POLICE_RED, Placement(offset(drone, 0, 1.4, 0)))
    graft(
        p,
        [
            [-12, -9],
            [12, -9],
            [10, -13],
            [-10, -13],
        ],
        [BAY_TOP - 2.5, BAY_TOP - 1.5],
        at,
    )


def build_sentinel(scene: Any) -> Any:
    """P07-R05, P16-R05: the Sentinel, a twin-bodied city hunter: a blue body and a red one joined
    by a membrane through its thorax, police-light glands on its back, a gun growth on each body's
    outer flank and a brood pouch at the nose, between the bodies."""

    def core(p: Any) -> None:
        _draw_body(p)
        _draw_gear(p)
        for s in SIDES:
            reactor_sac(p, [s * HULL_X, 1, -37], 3.6, BLUE if s > 0 else POLICE_RED)
        reactor_sac(p, [0, 2, -27], 3, BLUE)

    return build_boss_model(
        SENTINEL,
        scene,
        BLUE,
        {
            "core": core,
            "parts": {"gun-left": _hull_gun, "gun-right": _hull_gun, "drone-bay": _drone_bay},
            "turrets": {"gun-left": _hull_gun_turret, "gun-right": _hull_gun_turret},
        },
    )
