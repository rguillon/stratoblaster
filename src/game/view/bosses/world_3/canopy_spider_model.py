"""P09-R09, 3-2: the Canopy Spider. Ported from `view/bosses/world-3/canopy-spider-model.ts`.
Logical pixels, nose +Z, Y up (towards the camera). A walker-ship hanging over the canopy: an
armoured cephalothorax carrying the head, its eyes and fangs at the front and the crown emitter
on its back; a big abdomen behind it, the egg sac (a part) at its tip; four legs stepping in turn
(limbs on joints, see `canopy-spider-legs.ts`)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_3.canopy_spider import CANOPY_SPIDER, SPIDER_CROWN
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_greebles import seam, vent
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
    socket,
)
from game.view.bosses.world_3.canopy_spider_legs import (
    SPIDER_RED,
    leg_gun_pod,
    leg_limbs,
    leg_points,
)
from game.view.bosses.world_3.canopy_spider_sac import egg_sac
from game.view.bosses.world_3.jungle_flesh import F, table, vein_to
from game.view.bosses.world_3.toucan_jungle import moss, sagging, vine
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import ROUND_SECTION, SHELL_SECTION, RibSpec, ribs
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The cephalothorax, back to front (loft stations: z, half width, bottom, top).
THORAX = table(
    [
        [-10, 12, -1, 11],
        [0, 17, -3, 15],
        [12, 16, -3, 15],
        [22, 12, -2, 12.5],
        [30, 7, 0, 8.5],
    ]
)
# The abdomen, from its tip (where the egg sac hangs) to its waist.
ABDOMEN = table(
    [
        [-47, 5, 3, 9],
        [-40, 14, -1, 19],
        [-34, 18, -2, 21],
        [-20, 18, -2, 21],
        [-12, 14, 0, 18],
        [-7, 8, 3, 12],
    ]
)
# The red hourglass on the abdomen's back (right half, front to back).
HOURGLASS = table(
    [
        [0, -20],
        [5, -21],
        [1, -27],
        [5, -33],
        [0, -34],
        [-5, -33],
        [-1, -27],
        [-5, -21],
    ]
)
# The eyes: the two big ones at the front, then the smaller ones (x, height, z, radius).
EYES = table(
    [
        [3.6, 6.8, 28.6, 2.3],
        [5.6, 7.4, 24, 1.5],
        [2.4, 11, 22.4, 1.2],
    ]
)


def draw_body(p: EnemyParts) -> None:
    """The cephalothorax and the abdomen: dark armour, the red hourglass, moss on the plates."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a living spider: a chitin-shelled cephalothorax, a swollen purple abdomen with bone
    # ribs and pulsing veins, a sinew waist; metal plates and vents grafted on.
    flesh.loft(SHELL_SECTION, THORAX, F.purple, None, None)
    flesh.loft(ROUND_SECTION, ABDOMEN, F.purple, None, None)
    flesh.box([12, 6, 6], F.sinew, Placement([0, 2, -8]))
    ribs(flesh, [-18, -28, -38], RibSpec(15, 6, 15.4, 0.8), F.bone)
    for s in SIDES:
        vein_to(
            p,
            [[s * 3, 21.2, -14], [s * 9, 19, -44]],
            [s * 4, 0.6, 0],
            SPIDER_RED,
            1.1,
        )
    neon.slab(HOURGLASS, [21.05, 21.35], SPIDER_RED, Placement([0, -0.3, 0]))
    for s in SIDES:
        seam(hull, [s * 5, 12], [s * 4, -6], [12, 0.8, 0.6], H.dark)
        seam(hull, [s * 8, -19], [s * 8, -35], [21, 1, 0.5], SHADE["edge"])
        vent(hull, [s * 7, 11, 14], [3, 5], 3, s * 0.1)
        vine(hull, sagging([s * 17, 12, -14], [s * 15, 9, -42], 5, 3), 0.5)
    moss(hull, [10, 20.6, -36], 3.4, 0.4)
    moss(hull, [-10, 20.6, -22], 3.2, 1.9)
    moss(hull, [-6, 12.2, 8], 3, 3.3)
    hull.box([5, 1.4, 4], SHADE["patch"], Placement([-9, 20.4, -38], 0.4))


def draw_head(p: EnemyParts) -> None:
    """The head: the red neon eyes, the fangs under them, the hips' sockets on the thorax."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    for s in SIDES:
        for eye_def in EYES:
            x = eye_def[0]
            y = eye_def[1]
            z = eye_def[2]
            r = eye_def[3]
            eye: Vec3 = [s * x, y, z]
            flesh.cylinder(
                r * 1.3,
                0.8,
                7,
                F.crimson,
                Placement(offset(eye, 0, -0.6, 0), 0, 0.7),
            )
            neon.cylinder(r, 0.7, 8, SPIDER_RED, Placement(eye, 0, 0.7))
            charge.cylinder(
                r * 0.45,
                0.3,
                6,
                WHITE,
                Placement(offset(eye, 0, 0.45, 0.35), 0, 0.7),
            )
        # The fangs (chelicerae), curving down in front of the head.
        # P16-R06: flesh chelicerae, bone fangs, a metal cap grafted on each.
        flesh.box([3.4, 4, 7], F.sinew, Placement([s * 3.6, -1, 31], 0, 0.5), F.crimson)
        hull.box([3.6, 1, 3], H.panel, Placement([s * 3.6, 1.4, 29.5], 0, 0.5))
        flesh.cylinder(1.1, 5, 4, F.bone, Placement([s * 3.6, 0.5, 36], 0, 2.2), 0)


def draw_crown(p: EnemyParts) -> None:
    """The hips' sockets, and the crown emitter on the thorax's back (the core's spirals)."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    for leg in ["fore-left", "fore-right", "aft-left", "aft-right"]:
        hip = leg_points(leg)[0]
        socket(hull, offset(hip, 0, -4, 0), 4.6, 5)
    crowns = [boss_point(m[0], m[1], m[2]) for m in SPIDER_CROWN]
    if len(crowns) == 0:
        return
    crown = crowns[0]
    hull.lathe(
        [[6, 0], [5.6, 2.4], [3.6, 4.6], [2.4, 5]],
        8,
        H.panel,
        Placement(offset(crown, 0, -6.6, 0), math.pi / 8),
    )
    neon.ring(5.9, 0.6, 8, SPIDER_RED, Placement(offset(crown, 0, -5.8, 0), math.pi / 8))
    hull.cylinder(2.2, 1.2, 8, H.dark, Placement(offset(crown, 0, -1.8, 0)))
    charge.cylinder(1.8, 0.6, 8, WHITE, Placement(offset(crown, 0, -0.6, 0)))
    muzzle(crown, "ring")
    for s in SIDES:
        hull.box(
            [1.4, 3, 6],
            SHADE["edge"],
            Placement(offset(crown, s * 4.4, -5, -1), 0, 0, s * 0.3),
        )
    hull.box([3, 1.4, 8], H.dark, Placement(offset(crown, 0, -6.4, -8), 0, QUARTER / 6))


def canopy_spider_core(p: EnemyParts) -> None:
    """The core of the Canopy Spider: its body, head and crown."""
    draw_body(p)
    draw_head(p)
    draw_crown(p)


def build_canopy_spider(scene: Any) -> Any:
    """P09-R09: the Canopy Spider, a four-legged walker-ship hanging over the canopy, its legs
    stepping in turn, red neon eyes, moss and vines on its armour."""
    parts: dict[str, Any] = {
        "leg-fore-left": leg_gun_pod,
        "leg-fore-right": leg_gun_pod,
        "leg-aft-left": leg_gun_pod,
        "leg-aft-right": leg_gun_pod,
        "egg-sac": egg_sac,
    }
    return build_boss_model(
        CANOPY_SPIDER,
        scene,
        SPIDER_RED,
        {"core": canopy_spider_core, "parts": parts, "limbs": leg_limbs()},
    )
