"""P09-R09, 3-1: the Mangrove Croc's jaws (on their hinges, D-061), its jaw cannon and its side
pontoons. Logical pixels, nose +Z,
Y up; the left jaw and pontoon (the screen's left, -X on the playfield) are drawn at +X."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_3.mangrove_croc import (
    CROC_JAW,
    CROC_JAW_CANNON,
    CROC_JAW_SWING,
    CROC_PONTOON_GUNS,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import (
    JUNGLE_FLESH,
    F,
    gland,
    sac,
    sign_of,
    table,
    vein_to,
)
from game.view.bosses.world_3.mangrove_croc_jungle import barrel_to, moss, vine
from game.view.enemies.enemy_shapes import POD_SECTION, flip_x, side_stripe
from render.geometry.organic import RibSpec, ribs
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The Mangrove Croc's green neon (P09-R09).
CROC_GREEN = BOSS_LOOK.neon["mangrove-croc"]

# The left jaw seen from above, from its hinge (x across, z along), as it is shut: wide at the
# hinge, its inner edge along the croc's centre line, tapering to the tip.
JAW = table(
    [
        [-6.5, 0],
        [4, 0],
        [5, 6],
        [3.5, 16],
        [0, 24.5],
        [-2, 26.5],
        [-4.5, 25],
        [-6.5, 14],
    ]
)
# The jaw's heights: its bottom, its waist and its top.
JAW_Y = [0, 2, 5]
# How far along the jaw (z from the hinge) its teeth stand on the inner edge.
TEETH = [5, 10, 15, 20, 24]


def turn_about(at: Vec3, p: Vec3, yaw: float) -> Vec3:
    """`p` (from `at`) turned by `yaw` around +Y, then moved to `at`."""
    c = math.cos(yaw)
    k = math.sin(yaw)
    return [at[0] + p[0] * c + p[2] * k, at[1] + p[1], at[2] - p[0] * k + p[2] * c]


def scaled_about(outline: list[OutlinePoint], k: float, centre: list[float]) -> list[OutlinePoint]:
    """`outline` shrunk by `k` around `centre`."""
    cx = centre[0]
    cz = centre[1]
    return [[cx + (x - cx) * k, cz + (z - cz) * k] for x, z in outline]


def draw_jaw(s: float) -> Any:
    """A jaw (side `s`, +1 the left one at +X), drawn half open as at rest: an armoured wedge with
    a row of teeth along its inner edge, green neon along its outer edge and moss on its back."""

    def draw(p: EnemyParts) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        hinge = CROC_JAW.hinge
        at = boss_point(s * -abs(hinge[0]), hinge[1], 0)
        place = Placement(at, (s * CROC_JAW_SWING.amplitudeDeg * math.pi) / 180)
        outline = JAW if s > 0 else flip_x(JAW)
        # P16-R05: a fleshy jaw, bone fangs along it, a metal plate grafted on its back.
        flesh.bevel_slab(outline, JAW_Y, [0.8, 1.2], F.sinew, place, JUNGLE_FLESH)
        hull.box(
            [5, 0.8, 8],
            H.panel,
            Placement(turn_about(at, [s * -1.5, JAW_Y[2], 4], place.yaw), place.yaw),
            H.base,
        )
        for z in TEETH:
            edge = -6.6 + max(0, z - 14) * 0.25
            flesh.box(
                [2.2, 2.4, 1.6],
                F.bone,
                Placement(turn_about(at, [s * edge, 0.4, z], place.yaw), place.yaw),
            )
        outer = outline[1:4]
        for i in range(len(outer) - 1):
            a = outer[i]
            b = outer[i + 1]
            dx = b[0] - a[0]
            dz = b[1] - a[1]
            neon.box(
                [0.9, 0.6, math.hypot(dx, dz)],
                CROC_GREEN,
                Placement(
                    turn_about(
                        at,
                        [(a[0] + b[0]) / 2, JAW_Y[2] - 0.8, (a[1] + b[1]) / 2],
                        place.yaw,
                    ),
                    place.yaw + math.atan2(dx, dz),
                ),
            )
        moss(hull, scaled_about(table(outline), 0.45, [s * -1.5, 6]), JAW_Y[2])

    return draw


# The jaws (D-061): each drawn on its hinge, they open and close with it; they go with the core.
CROC_JAWS = {
    "jaw-left": {"draw": draw_jaw(1)},
    "jaw-right": {"draw": draw_jaw(-1)},
}


def jaw_cannon(p: EnemyParts, at: Vec3) -> None:
    """The jaw cannon (P09-R09) in the croc's throat between the jaws: a ribbed housing with a neon
    collar, its barrel reaching for the jaws' tips, a charge light glowing in its maw."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    if len(CROC_JAW_CANNON) == 0:
        return
    tip = CROC_JAW_CANNON[0]
    axis = boss_point(tip[0], tip[1], tip[2])[1]
    back = offset(at, 0, axis, -8)
    # P16-R05: a throat gland swelling behind the grafted cannon, veins feeding it.
    sac(p, offset(back, 0, 0, -2), 5, F.crimson)
    gland(p, offset(back, 0, 2.6, -2), 1.8, CROC_GREEN)
    hull.cylinder(4.4, 9, 8, H.panel, Placement(back, 0, QUARTER), 3.4)
    hull.cylinder(5, 1.6, 8, H.dark, Placement(offset(back, 0, 0, 1), 0, QUARTER))
    neon.ring(3.6, 0.9, 8, CROC_GREEN, Placement(offset(back, 0, 0, 7.4), 0, QUARTER))
    charge.box([4, 0.5, 3], WHITE, Placement(offset(at, 0, axis + 3.3, -4)))
    barrel_to(p, tip, [1.8, 8])


# A pontoon's float (loft stations from its centre: z, half width, bottom, top).
FLOAT = table(
    [
        [-22, 3, 1, 4],
        [-16, 7.5, -2, 7],
        [2, 8.5, -2, 7.5],
        [11, 6.5, -1, 6.5],
        [14, 3, 1, 4.5],
    ]
)


def pontoon(p: EnemyParts, at: Vec3) -> None:
    """A side pontoon (P09-R09): a long armoured float with its twin fan guns at its bow, a green
    light along its outer side, moss on its back and a vine trailing from it."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    s = sign_of(at[0])
    stations = [[z + at[2], w, b, t] for z, w, b, t in FLOAT]
    origin: Vec3 = [at[0], 0, 0]
    # P16-R05: a swollen float-bladder, ridged like a croc's flank, plated at its bow.
    flesh.loft(POD_SECTION, stations, JUNGLE_FLESH, Placement(origin))
    ribs(
        flesh,
        [at[2] - 12, at[2] - 6, at[2]],
        RibSpec(8, 2, 5.6, 0.6),
        F.bone,
        Placement(origin),
    )
    vein_to(p, [offset(at, 0, 7.6, -16), offset(at, 0, 7.6, 8)], [0, 0.8, 0], CROC_GREEN)
    side = 3 if s <= 0 else 1
    neon.loft(
        side_stripe(POD_SECTION, side, [0.15, 0.45], 1.04),
        stations[1:4],
        CROC_GREEN,
        Placement(origin),
        LoftOptions(True),
    )
    hull.box([12, 1.6, 6], H.dark, Placement(offset(at, 0, 7.2, -4)), SHADE["edge"])
    moss(
        hull,
        [
            [at[0] - 4, at[2] - 14],
            [at[0] + 4, at[2] - 12],
            [at[0] + 3, at[2] - 4],
            [at[0] - 3, at[2] - 6],
        ],
        7.2,
    )
    vine(hull, offset(at, s * 7, 5, -10), offset(at, s * 6, 4, 4), 4)
    guns = CROC_PONTOON_GUNS if s < 0 else mirror(CROC_PONTOON_GUNS)
    for tip in guns:
        barrel_to(p, tip, [1.3, 7])
    hull.box([8, 3, 4], H.dark, Placement(offset(at, 0, 2.6, 8.5)), H.panel)
