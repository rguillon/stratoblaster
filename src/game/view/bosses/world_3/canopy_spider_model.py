# Copyright (c) 2026 Renaud Guillon
"""FB-CANOPY-SPIDER-01 to FB-CANOPY-SPIDER-06, 3-2: the Canopy Spider.

Logical pixels, nose +Z, Y up (towards the camera). A walker-ship hanging over the canopy: an
armoured cephalothorax carrying the head, its eyes and fangs at the front and the crown emitter
on its back; a big abdomen behind it, the egg sac (a part) at its tip; four legs stepping in
turn. The plating of both bodies is the armour it sheds (FB-CANOPY-SPIDER-12, FB-CANOPY-SPIDER-13,
D-254): drawn apart from the bodies, which are flattened under it.
"""

import math

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
from render.geometry.organic import RibSpec, ribs
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


# The cephalothorax, back to front (loft stations: z, half width, bottom, top).
THORAX = table([
    [-10, 12, -1, 11],
    [0, 17, -3, 15],
    [12, 16, -3, 15],
    [22, 12, -2, 12.5],
    [30, 7, 0, 8.5],
])
# The abdomen, from its tip (where the egg sac hangs) to its waist.
ABDOMEN = table([
    [-47, 5, 3, 9],
    [-40, 14, -1, 19],
    [-34, 18, -2, 21],
    [-20, 18, -2, 21],
    [-12, 14, 0, 18],
    [-7, 8, 3, 12],
])
# Each body is drawn in two: its lower half (the core's) up to a flat top, and its plating (the
# armour it sheds, FB-CANOPY-SPIDER-12 and FB-CANOPY-SPIDER-13) from `PLATING_SINK` under that top
# up to the body's own top: the abdomen's back plating over its belly, the cephalothorax's spine
# plating over its lower shell.
BELLY_TOP = 7
SHELL_TOP = 4.6
PLATING_SINK = 0.3
# The bodies' sections in two halves, counter-clockwise seen from the nose: `ROUND_SECTION` split
# at its widest for the abdomen, `SHELL_SECTION` low on its flanks for the thorax (under its eyes).
BELLY_SECTION = table([[0.4, 0], [0.9, 0.45], [1, 1], [-1, 1], [-0.9, 0.45], [-0.4, 0]])
BACK_SECTION = table([[1, 0], [0.65, 0.78], [0, 1], [-0.65, 0.78], [-1, 0]])
LOWER_SHELL_SECTION = table([[0.7, 0], [1, 0.48], [0.86, 1], [-0.86, 1], [-1, 0.48], [-0.7, 0]])
UPPER_SHELL_SECTION = table([
    [0.86, 0],
    [0.75, 0.31],
    [0.3, 0.79],
    [0, 1],
    [-0.3, 0.79],
    [-0.75, 0.31],
    [-0.86, 0],
])
# The red hourglass on the abdomen's back (right half, front to back).
HOURGLASS = table([
    [0, -20],
    [5, -21],
    [1, -27],
    [5, -33],
    [0, -34],
    [-5, -33],
    [-1, -27],
    [-5, -21],
])
# The eyes: the two big ones at the front, then the smaller ones (x, height, z, radius).
EYES = table([
    [3.6, 6.8, 28.6, 2.3],
    [5.6, 7.4, 24, 1.5],
    [2.4, 11, 22.4, 1.2],
])
# The crown emitter's stalk: its radius, and where it stands on the lower shell.
STALK_RADIUS = 3
STALK_FOOT = SHELL_TOP - 0.2


def lower_stations(stations: Any, top: float) -> Any:
    """Return `stations` flattened to `top`: the lower half of a body, the core's."""
    return [[st[0], st[1], st[2], top] for st in stations]


def plating_stations(stations: Any, top: float) -> Any:
    """Return `stations` from `PLATING_SINK` under `top` up to their own top: a body's plating."""
    return [[st[0], st[1], top - PLATING_SINK, st[3]] for st in stations]


def draw_body(p: EnemyParts) -> None:
    """Draw the lower bodies: the belly and the lower shell, flat-topped, the waist between them.

    FB-CANOPY-SPIDER-02: a living spider, a sinew waist between its two bodies; the vines hang on
    the belly's flanks. Their plating is drawn apart (`draw_back_plating`, `draw_spine_plating`).
    """
    flesh = p.flesh
    flesh.loft(LOWER_SHELL_SECTION, lower_stations(THORAX, SHELL_TOP), F.graphite, None, None)
    flesh.loft(BELLY_SECTION, lower_stations(ABDOMEN, BELLY_TOP), F.graphite, None, None)
    flesh.box([12, 6, 6], F.sinew, Placement([0, 2, -8]))
    for s in SIDES:
        vine(p.hull, sagging([s * 17, 12, -14], [s * 15, 9, -42], 5, 3), 0.5)


def draw_back_plating(p: EnemyParts) -> None:
    """Draw the abdomen's plating (FB-CANOPY-SPIDER-12): the armour it sheds first.

    The chitin over the belly, from just under its flat top up to the abdomen's back, its bone ribs
    and pulsing veins, the red hourglass, the grafted seams, the moss and the patch on it.
    """
    hull = p.hull
    flesh = p.flesh
    flesh.loft(BACK_SECTION, plating_stations(ABDOMEN, BELLY_TOP), F.graphite, None, None)
    ribs(flesh, [-18, -28, -38], RibSpec(15, BELLY_TOP + 0.2, 14.2, 0.8), F.bone)
    for s in SIDES:
        vein_to(
            p,
            [[s * 3, 21.2, -14], [s * 9, 19, -44]],
            [s * 4, 0.6, 0],
            SPIDER_RED,
            1.1,
        )
        seam(hull, [s * 8, -19], [s * 8, -35], [21, 1, 0.5], SHADE["edge"])
    p.neon.slab(HOURGLASS, [21.05, 21.35], SPIDER_RED, Placement([0, -0.3, 0]))
    moss(hull, [10, 20.6, -36], 3.4, 0.4)
    moss(hull, [-10, 20.6, -22], 3.2, 1.9)
    hull.box([5, 1.4, 4], SHADE["patch"], Placement([-9, 20.4, -38], 0.4))


def draw_eyes(p: EnemyParts) -> None:
    """Draw the red neon eyes on the shell: two big ones at the front, the smaller ones behind."""
    for s in SIDES:
        for eye_def in EYES:
            x = eye_def[0]
            y = eye_def[1]
            z = eye_def[2]
            r = eye_def[3]
            eye: Vec3 = [s * x, y, z]
            p.flesh.cylinder(
                r * 1.3,
                0.8,
                7,
                F.slate,
                Placement(offset(eye, 0, -0.6, 0), 0, 0.7),
            )
            p.neon.cylinder(r, 0.7, 8, SPIDER_RED, Placement(eye, 0, 0.7))
            p.charge.cylinder(
                r * 0.45,
                0.3,
                6,
                WHITE,
                Placement(offset(eye, 0, 0.45, 0.35), 0, 0.7),
            )


def draw_spine_plating(p: EnemyParts) -> None:
    """Draw the cephalothorax's plating (FB-CANOPY-SPIDER-13): the armour it sheds second.

    The ridged chitin shell over the lower shell, from just under its flat top up to the ridge, the
    eyes at its front, the grafted seams, vents and moss on it.
    """
    hull = p.hull
    p.flesh.loft(UPPER_SHELL_SECTION, plating_stations(THORAX, SHELL_TOP), F.graphite, None, None)
    draw_eyes(p)
    for s in SIDES:
        seam(hull, [s * 5, 12], [s * 4, -6], [12, 0.8, 0.6], H.dark)
        vent(hull, [s * 7, 11, 14], [3, 5], 3, s * 0.1)
    moss(hull, [-6, 12.2, 8], 3, 3.3)


def draw_head(p: EnemyParts) -> None:
    """Draw the fangs under the head (its eyes ride the spine plating, `draw_eyes`)."""
    for s in SIDES:
        # The fangs (chelicerae), curving down in front of the head.
        # FB-CANOPY-SPIDER-02: flesh chelicerae, bone fangs, a metal cap grafted on each.
        p.flesh.box([3.4, 4, 7], F.sinew, Placement([s * 3.6, -1, 31], 0, 0.5), F.slate)
        p.hull.box([3.6, 1, 3], H.panel, Placement([s * 3.6, 1.4, 29.5], 0, 0.5))
        p.flesh.cylinder(1.1, 5, 4, F.bone, Placement([s * 3.6, 0.5, 36], 0, 2.2), 0)


def draw_crown(p: EnemyParts) -> None:
    """Draw the hips' sockets, and the crown emitter on the thorax's back (the core's spirals).

    The emitter stands on a stalk rooted in the lower shell, through the spine plating, so that it
    stays up once the plating is shed (BOSS-52).
    """
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
    base = offset(crown, 0, -6.6, 0)
    hull.cylinder(
        STALK_RADIUS,
        base[1] + 0.4 - STALK_FOOT,
        8,
        H.dark,
        Placement([crown[0], STALK_FOOT, crown[2]], math.pi / 8),
    )
    hull.lathe(
        [[6, 0], [5.6, 2.4], [3.6, 4.6], [2.4, 5]],
        8,
        H.panel,
        Placement(base, math.pi / 8),
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
    """Add the core of the Canopy Spider: its bodies, head and crown (its plating drawn apart)."""
    draw_body(p)
    draw_head(p)
    draw_crown(p)


def build_canopy_spider(scene: Any) -> Any:
    """FB-CANOPY-SPIDER-01, FB-CANOPY-SPIDER-06: the Canopy Spider.

    A four-legged walker-ship hanging over the canopy, its legs stepping in turn, red neon eyes,
    moss and vines on its armour. The plating of its abdomen (`back`) and of its cephalothorax
    (`spine`) is the armour it sheds.
    """
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
        {
            "core": canopy_spider_core,
            "parts": parts,
            "limbs": leg_limbs(),
            "armour": {
                "back": {"whole": draw_back_plating},
                "spine": {"whole": draw_spine_plating},
            },
        },
    )
