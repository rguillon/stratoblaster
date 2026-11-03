# Copyright (c) 2026 Renaud Guillon
"""MB-TOUCAN-01 to MB-TOUCAN-06, 3-2: the Toucan.

Logical pixels, nose +Z, Y up (towards the camera). A stubby gunship: a round black body, short
wings carrying the fan pods, a fanned tail, and the huge bright beak (its cannon, a part) in front
of its head. Its back plating, two plates either side of the spine ridge over the flattened body,
is the armour it sheds (MB-TOUCAN-12, D-254): `draw_plating`.
"""

from game.config.bosses.world_3.toucan import TOUCAN, TOUCAN_CHEEK_GUNS, TOUCAN_CREST
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import (
    mirrored,
    strip,
)
from game.view.bosses.mini_boss_greebles import seam, vent
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
    socket,
)
from game.view.bosses.world_3.jungle_flesh import F, sinew, spine, table
from game.view.bosses.world_3.toucan_jungle import moss, sagging, vine
from game.view.bosses.world_3.toucan_parts import (
    TOUCAN_ORANGE,
    TOUCAN_YELLOW,
    beak,
    wing_pod,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import ROUND_SECTION
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Rgb = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The body's shape along the centre line, tail to head (loft stations: z, half width, bottom, top).
# Its back from `PLATING_FROM` to the head is the plating (MB-TOUCAN-12).
BODY = table([
    [-36, 5, 0, 5],
    [-26, 11, -2, 9.5],
    [-10, 16, -4, 13],
    [6, 17, -4, 15],
    [15, 14.5, -3, 14.2],
    [21, 10.6, -1.5, 12.6],
])
# Where the plating starts (z): the tail stub behind it stays low.
PLATING_FROM = -26
# The keel: the body as drawn (the core), flattened to `KEEL_TOP` under the plating, whose plates
# start at `PLATE_BOTTOM`, sunk into it.
KEEL_TOP = 4.3
PLATE_BOTTOM = 4.0
# The heights of the orange neon strip along a plate's flank, on its bottom edge.
FLANK_STRIP = [PLATE_BOTTOM, PLATE_BOTTOM + 0.8]
KEEL = table([[st[0], st[1], st[2], KEEL_TOP if st[0] >= PLATING_FROM else st[3]] for st in BODY])
# The spine ridge along the back, between the plates: `RIDGE_SHARE` of the body's half width, from
# `RIDGE_BOTTOM` up to the body's back, tapering to a point on the tail stub. It carries the crest.
RIDGE_SHARE = 0.2
RIDGE_BOTTOM = 3.5
RIDGE = table(
    [[PLATING_FROM - 2, 0, KEEL_TOP, KEEL_TOP]]
    + [[st[0], st[1] * RIDGE_SHARE, RIDGE_BOTTOM, st[3]] for st in BODY if st[0] >= PLATING_FROM]
)
# A plate's loft stations (the body's over the keel) and its cross-section (the right one, counter-
# clockwise seen from the nose): the body's skin from the ridge over the shoulder down to its
# flank, closed by a flat bottom on the keel and a wall along the ridge.
PLATES = table([[st[0], st[1], PLATE_BOTTOM, st[3]] for st in BODY if st[0] >= PLATING_FROM])
PLATE_SECTION = table([
    [RIDGE_SHARE, 0],
    [0.96, 0],
    [1.0, 0.22],
    [0.65, 0.83],
    [RIDGE_SHARE, 1.0],
])
# The cream bib under its head (the lower sides of the body's last band).
BIB = [0.7, 0.64, 0.42]
BIB_SIDES = [0, 1, 7, 8]
BIB_BAND = len(BODY) - 2
# The wings seen from above (right half, front to back), the pods at their ends.
WINGS = mirrored([
    [0, 13],
    [14, 12],
    [26, 9],
    [30, 4],
    [30, -9],
    [24, -15],
    [12, -17],
    [0, -17],
])
# The tail's fan of feathers seen from above (right half, from the body back).
TAIL = mirrored([[0, -30], [8, -32], [11, -45], [5, -48], [0, -44]])


def body_paint(side: int, band: int) -> Any:
    """Return the body's paint: the bib on the lower sides of its last band."""
    if band == BIB_BAND and side in BIB_SIDES:
        return BIB
    return None


def draw_body(p: EnemyParts) -> None:
    """Draw the body: the flattened keel with its cream bib, the spine ridge and the ribcage.

    The plating over it is drawn apart (`draw_plating`).
    """
    flesh = p.flesh
    # MB-TOUCAN-02: a round, living bird's body of dark flesh, a bone ribcage over its back.
    flesh.loft(
        ROUND_SECTION,
        KEEL,
        F.graphite,
        None,
        LoftOptions(False, body_paint),
    )
    flesh.loft(ROUND_SECTION, RIDGE, F.graphite)
    path: list[Vec3] = [[0, st[3] + 0.3, st[0]] for st in BODY[1:]]
    # The ribs stand from the keel's widest flank (BOSS-52), their arches over the plating.
    spine(
        p,
        path,
        {"at": [-20, -12, -4], "halfWidth": 13, "y": 1, "height": 12.8},
        TOUCAN_ORANGE,
    )


def plate_section(s: float) -> Any:
    """Return the plate section of side `s` (+1 the right one at +X), counter-clockwise."""
    if s > 0:
        return PLATE_SECTION
    n = len(PLATE_SECTION)
    return table([[-PLATE_SECTION[n - 1 - k][0], PLATE_SECTION[n - 1 - k][1]] for k in range(n)])


def draw_plate(p: EnemyParts, s: float) -> None:
    """Draw the plate on side `s` of the ridge: the body's back there, and what lies on it.

    Orange neon along its flank, a seam and a vent on its back, moss, and the eye on its cheek.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    p.flesh.loft(plate_section(s), PLATES, F.graphite)
    # Orange neon along the plate's bottom edge.
    strip(neon, [s * 15.6, 4], [s * 12, -20], 0.8, FLANK_STRIP, TOUCAN_ORANGE)
    seam(hull, [s * 6, 10], [s * 7, -22], [12.4, 0.8, 0.5], H.dark)
    vent(hull, [s * 9, 11.4, -14], [3.2, 6], 3, s * 0.12)
    if s > 0:
        moss(hull, [5, 14.2, -4], 4.2, 0.7)
    else:
        moss(hull, [-7, 11.6, -19], 3.4, 2.1)
    # MB-TOUCAN-03: the round neon eye on the cheek.
    eye: Vec3 = [s * 12.4, 8.6, 15]
    hull.cylinder(3.2, 0.8, 8, H.dark, Placement(eye, 0, 0, -s * QUARTER))
    neon.ring(
        3.3,
        0.9,
        8,
        TOUCAN_YELLOW,
        Placement(offset(eye, s * 0.4, 0, 0), 0, 0, -s * QUARTER),
    )
    charge.cylinder(
        1.5,
        0.5,
        8,
        WHITE,
        Placement(offset(eye, s * 0.6, 0, 0), 0, 0, -s * QUARTER),
    )


def draw_plating(p: EnemyParts) -> None:
    """Draw the back plating (MB-TOUCAN-12): the armour it sheds at its transformation.

    Two plates, one either side of the spine ridge, from just under the keel's top up to the body's
    back, from the tail stub to the head, the eyes on their cheeks. The racks lie folded under them.
    """
    for s in SIDES:
        draw_plate(p, s)


def draw_wings_and_tail(p: EnemyParts) -> None:
    """Draw the wings and the tail: dark, bevelled, neon on their edges, vines hanging from them."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # MB-TOUCAN-02: short, heavy membrane wings (still) on bone struts, a fan of bone quills.
    flesh.bevel_slab(WINGS, [-1.5, 0, 2], [0.8, 1], F.membrane, None, F.graphite)
    flesh.bevel_slab(TAIL, [0.5, 1.5, 3], [0.4, 0.8], F.membrane, None, F.slate)
    for s in SIDES:
        for strut_end in [[30, 4], [30, -9], [24, -15]]:
            sinew(
                p,
                [[s * 4, 2.4, 0], [s * strut_end[0], 2.2, strut_end[1]]],
                [0, 0.6, 0],
                1,
                F.bone,
            )
        sinew(
            p,
            [[s * 2, 3.2, -30], [s * 10, 3.2, -45]],
            [0, 0.3, 0],
            0.7,
            F.bone,
        )
    for s in SIDES:
        strip(neon, [s * 14, 12.2], [s * 25.5, 9.4], 0.8, [1.9, 2.3], TOUCAN_YELLOW)
        strip(neon, [s * 8.5, -33], [s * 10.6, -44.5], 0.7, [2.9, 3.3], TOUCAN_ORANGE)
        seam(hull, [s * 18, 8], [s * 22, -14], [2, 0.6, 0.4], H.dark)
        vine(hull, sagging([s * 12, -0.5, -16.5], [s * 26, -0.5, -14.5], 5, 3.5))
        moss(hull, [s * 20, 2, -4], 3, s)
        reactor_sac(p, table([s * 4.5, 3, -36.2]), 2.8, table(TOUCAN_ORANGE), None, None)


def draw_head(p: EnemyParts) -> None:
    """Draw the head (MB-TOUCAN-03): the cheek guns, and the crest emitter on the spine ridge.

    The eyes are on the plating's cheeks (`draw_plate`).
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    for m in TOUCAN_CHEEK_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.box([4.4, 4, 7], H.panel, Placement([x, y - 2.4, z - 10]), H.base)
        hull.cylinder(1.2, 6.4, 6, H.dark, Placement([x, y, z - 7], 0, QUARTER))
        charge.cylinder(1.25, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)
    if len(TOUCAN_CREST) == 0:
        return
    crest = boss_point(TOUCAN_CREST[0][0], TOUCAN_CREST[0][1], TOUCAN_CREST[0][2])
    socket(hull, offset(crest, 0, -3.4, 0), 3.4, 1.6)
    neon.ring(3.5, 0.5, 8, TOUCAN_ORANGE, Placement(offset(crest, 0, -2.2, 0)))
    hull.cylinder(2.2, 1.2, 8, H.panel, Placement(offset(crest, 0, -1.8, 0)), 1.8)
    charge.cylinder(1.6, 0.6, 8, WHITE, Placement(offset(crest, 0, -0.6, 0)))
    muzzle(crest, "ring")
    hull.box(
        [2.6, 2.4, 7],
        SHADE["edge"],
        Placement(offset(crest, 0, -2.6, -7), 0, -0.25),
    )


def toucan_core(p: EnemyParts) -> None:
    """Add the core of the Toucan: its body, wings, tail and head (no plating)."""
    draw_body(p)
    draw_wings_and_tail(p)
    draw_head(p)


def build_toucan(scene: Any) -> Any:
    """MB-TOUCAN-01, MB-TOUCAN-06: the Toucan, a stubby gunship with a huge bright beak.

    It has yellow and orange neon, moss on its back and vines hanging from its wings. Its back
    plating is the armour it sheds (MB-TOUCAN-12).
    """
    parts: dict[str, Any] = {
        "pod-left": wing_pod,
        "pod-right": wing_pod,
        "beak": beak,
    }
    return build_boss_model(
        TOUCAN,
        scene,
        TOUCAN_YELLOW,
        {
            "core": toucan_core,
            "parts": parts,
            "armour": {"back": {"whole": draw_plating}},
        },
    )
