# Copyright (c) 2026 Renaud Guillon
"""MB-MANTIS-LANCER-01 to MB-MANTIS-LANCER-05: the Mantis Lancer, the Lab's L-4 mini boss.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A tall, narrow
praying mantis: a long abdomen under folded leaf wings, a plated thorax (the armour it sheds), a
long neck, a triangular head with great compound eyes, and two raptorial scythes raised forward
either side of the head, each carrying a laser turret (its gun mounts are drawn by
`build_boss_model`, BOSS-58).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.mantis_lancer import MANTIS_LANCER, ROTOR_AT
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_greebles import lamps
from game.view.bosses.mini_boss_shapes import offset, sign_of
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    gland,
    graft,
    polygon,
    rib_cage,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import SegmentedBody, carapace, segmented_body
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


GREEN = BOSS_LOOK.neon["mantis-lancer"]
# Its flesh: dark shades with a little moss green in them (BOSS-50 keeps moss green).
MOSS = [0.045, 0.07, 0.05]
LEAF = [0.05, 0.085, 0.055]

# The abdomen along Z, under its wings: tail, root, half width, belly and back.
ABDOMEN = [-64, -6, 14, -2, 6]
# The thorax under its plating: from the wings' root to the neck's root.
THORAX = [-9, 27, 11, -1.5, 5.5]
# The thorax plating (MB-MANTIS-LANCER-05): a ridged shell over the thorax, from `PLATING[0]` to its
# top `PLATING[1]`.
PLATING = [5.2, 11]
# The neck: from the thorax to the head, its axis `NECK_Y` high.
NECK = [24, 47]
NECK_Y = 6
# A folded wing (tegmen) seen from above, the right one: a long leaf over the abdomen.
WING = [
    [1, -2],
    [9, -6],
    [14, -18],
    [14, -40],
    [10, -58],
    [3, -68],
    [-1, -60],
    [-1, -10],
]
WING_Y = [5.5, 7.5, 8.6]
# The head seen from above: a triangle, its mouth at the front.
HEAD = [[0, 9], [6, 2], [12, -4], [9, -7], [-9, -7], [-12, -4], [-6, 2]]
HEAD_Y = [1.5, 4.5, 7]


def _draw_abdomen(p: Any) -> None:
    """Draw the abdomen (MB-MANTIS-LANCER-02): a long segmented body under two folded wings.

    The leaf wings lie over it, overlapping on its centre line, a green vein along each one's
    midrib; the hatch over its rotor sits on them.
    """
    tail, root, width, belly, back = ABDOMEN
    segmented_body(
        p.flesh,
        SegmentedBody(tail, root + 4, 5, width, belly, back, 0.25),
        MOSS,
    )
    for s in SIDES:
        wing = [[s * q[0], q[1]] for q in WING]
        p.flesh.bevel_slab(wing, WING_Y, [0.8, 1.2], LEAF, None, F.membrane)
        vein_line(p, [s * 4, WING_Y[2], -6], [s * 6, WING_Y[2], -60], [s * 4, 0.3, 0], 0.8, GREEN)
        for z in [-22, -38]:
            vein_line(
                p, [s * 7, WING_Y[2], z], [s * 13, WING_Y[2] - 0.6, z - 8], [0, 0.3, 0], 0.5, GREEN
            )
    # The plate the rotor's hatch sits on, grafted across the two wings.
    p.hull.cylinder(
        8.5, 0.8, 8, M.base, Placement([0, WING_Y[2] - 0.2, -ROTOR_AT[1]], math.pi / 8), 8
    )
    for s in SIDES:
        reactor_sac(p, [s * 5, 0.5, -62], 2.6, GREEN, MOSS)


def _draw_thorax(p: Any) -> None:
    """Draw the thorax under its plating and the long neck out to the head (MB-MANTIS-LANCER-02).

    The neck is plated with grafted rings, the neck turret's seat on it (its mount, BOSS-58).
    """
    tail, nose, width, belly, back = THORAX
    segmented_body(p.flesh, SegmentedBody(tail, nose, 2, width, belly, back, 0.2), F.sinew)
    neck: list[Any] = [
        [0, NECK_Y, NECK[0]],
        [0, NECK_Y + 1, (NECK[0] + NECK[1]) / 2],
        [0, NECK_Y, NECK[1]],
    ]
    tentacle(p, neck[0], neck[2], [0, 1.5, 0], [4.5, 3.4], F.sinew, 6)
    for z in [29, 39]:
        p.hull.cylinder(4.6, 2, 6, M.panel, Placement([0, NECK_Y, z], 0, math.pi / 2), 4.3)
    graft(p, polygon(6, 4.8), [NECK_Y + 2.4, 9], [0, 0, 33], {"color": M.base})
    spine(
        p, [0, NECK_Y + 3.6, 26], [0, NECK_Y + 3.4, 44], {"color": GREEN, "width": 0.8, "bow": 0.6}
    )
    # The scythes' roots: a sinew from each side of the neck's root, out under the scythe.
    for s in SIDES:
        tentacle(p, [s * 3, NECK_Y, 30], [s * 14, 8, 40], [s * 1, 3, 0], [3.2, 2.4], F.sinew, 5)
        p.hull.cylinder(3, 2.6, 6, M.dark, Placement([s * 14, 6, 40]), 2.6)


def _draw_legs(p: Any) -> None:
    """Draw its four walking legs, long and thin, jointed, splayed out of the thorax."""
    legs = [[10, 14, 32, 10, 46, 2], [8, 2, 34, -4, 50, -30]]
    for leg in legs:
        root_z = leg[1]
        for s in SIDES:
            knee = [s * leg[2], 11, leg[3]]
            foot = [s * leg[4], -3, leg[5]]
            tentacle(p, [s * leg[0], 2, root_z], knee, [0, 3, 0], [2, 1.3], F.sinew, 4)
            tentacle(p, knee, foot, [s * 2, 1, 0], [1.3, 0.3], F.bone, 4)
            p.vein.box([1, 0.6, 1], GREEN, Placement(offset(knee, 0, 1.2, 0)))


def _draw_plating(p: Any) -> None:
    """Draw the thorax plating (MB-MANTIS-LANCER-05): the armour it sheds at its transformation.

    A ridged carapace over the thorax, bone ribs across it, a green vein down its spine and a gland
    either side; the orbs lie folded under it.
    """
    tail = THORAX[0]
    nose = THORAX[1]
    carapace(
        p.flesh,
        SegmentedBody(tail - 1, nose + 1, 2, 16, PLATING[0], PLATING[1], 0.15),
        [M.panel, LEAF],
    )
    rib_cage(p, [4, 16], {"halfWidth": 13, "y": 7.5, "height": 3.6, "thickness": 0.9})
    spine(p, [0, PLATING[1] - 0.2, -6], [0, PLATING[1] - 0.2, 24], {"color": GREEN, "width": 1})
    for s in SIDES:
        gland(p, [s * 11, 8.6, 9], 1.6, GREEN)
        vein_line(p, [s * 3, 10.6, 14], [s * 11, 9.2, 9], [0, 0.5, 0], 0.7, GREEN)


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the abdomen rotor (BOSS-58): an armoured cap, a seam of light round."""
    at = [0, 0, -ROTOR_AT[1]]
    y = WING_Y[2] + 0.4
    p.hull.cylinder(6, 1.6, 8, M.panel, Placement(offset(at, 0, y, 0), math.pi / 8), 5.4)
    p.hull.cylinder(3.8, 1, 8, M.base, Placement(offset(at, 0, y + 1.6, 0), math.pi / 8), 3)
    p.neon.ring(5.8, 0.25, 8, GREEN, Placement(offset(at, 0, y + 1.2, 0), math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = [0, WING_Y[2] + 0.2, -ROTOR_AT[1]]
    p.hull.ring(5.6, 1, 16, M.base, Placement(at))
    p.neon.ring(5.6, 0.3, 16, GREEN, Placement(offset(at, 0, 1, 0)))


def _head(p: Any, at: Vec3) -> None:
    """Add the head (MB-MANTIS-LANCER-03): a flat triangle, its great compound eyes on its corners.

    Its twin gun sits in the mouth at its point (its mount, BOSS-58); feelers sweep back over it.
    """
    p.flesh.bevel_slab(HEAD, HEAD_Y, [1, 1.6], F.sinew, Placement(at), MOSS)
    graft(p, polygon(3, 5, [1.4, 0.9]), [HEAD_Y[2] - 0.2, HEAD_Y[2] + 0.6], offset(at, 0, 0, -2))
    for s in SIDES:
        eye = offset(at, s * 10.5, 3.5, -4.5)
        p.flesh.cylinder(3.6, 1.6, 6, F.graphite, Placement(eye))
        eyes(p, offset(eye, 0, 1.2, 0), {"count": 1, "size": 3}, GREEN)
        tentacle(
            p, offset(at, s * 2, 6.5, 2), offset(at, s * 9, 13, -12), [s * 4, 3, 6], [0.5, 0.1]
        )
        eyes(p, offset(at, s * 2.2, HEAD_Y[2], -3.5), {"count": 1, "size": 0.7}, GREEN)
    # The mandibles under the mouth.
    for s in SIDES:
        tentacle(p, offset(at, s * 3.5, 2.5, 6), offset(at, s * 1, 2, 10.5), [s, 0, 0], [1.2, 0.1])


# A scythe's blade seen from above, the left one (+X), round its part's centre: a crescent of bone
# folded forward from the knee, its hook bent back in at the front; its inner edge toothed.
BLADE: list[Any] = [
    [2, 2],
    [6.5, 8],
    [7.5, 15],
    [6, 21],
    [2, 25],
    [-3, 24.5],
    [-1, 22],
    [2, 19],
    [3, 14],
    [2, 8],
    [-1, 4],
]
BLADE_Y = [5.2, 6.8, 8]
# Where its teeth stand on the blade's inner edge, pointing in towards the head.
TEETH: list[Any] = [[2.2, 9], [3, 13], [2.6, 17], [1.4, 20.5]]


def _scythe(p: Any, at: Vec3) -> None:
    """Add a scythe (MB-MANTIS-LANCER-03): a raised raptorial foreleg, its laser turret on its knee.

    A thick femur rising from the neck's side to its armoured knee under the turret (its mount,
    BOSS-58), and the toothed tibia folded forward like a blade, its hook at the front.
    """
    s = sign_of(at[0])
    knee = offset(at, 0, 8.6, 2)
    root = offset(at, -s * 12, 2.5, -9)
    tentacle(p, root, knee, [0, 4, 0], [3.6, 3], F.sinew, 6)
    vein_line(p, offset(root, 0, 3.2, 0), offset(knee, 0, 2.8, 0), [0, 3, 0], 0.8, GREEN)
    barbs(
        p, offset(at, -s * 6, 9.5, -3), {"count": 2, "spacing": 3, "size": 2.4, "dir": [0, 1, -0.4]}
    )
    # The knee's armoured collar the turret sits on.
    p.hull.cylinder(5, 2.6, 8, M.panel, Placement(offset(at, 0, 8.4, 2), math.pi / 8), 4.4)
    p.neon.ring(5.1, 0.4, 8, GREEN, Placement(offset(at, 0, 9.4, 2), math.pi / 8))
    # The tibia: from under the knee down to the blade.
    tentacle(p, offset(at, 0, 8.6, 3), offset(at, s * 3.5, BLADE_Y[1], 8), [0, 1, 0], [2.6, 2])
    blade = [[s * q[0], q[1]] for q in BLADE]
    p.flesh.bevel_slab(blade, BLADE_Y, [0.6, 0.9], F.bone, Placement(at), F.sinew)
    vein_line(
        p,
        offset(at, s * 6.4, BLADE_Y[2], 9),
        offset(at, s * 4.6, BLADE_Y[2], 21),
        [s * 1.5, 0, 0],
        0.6,
        GREEN,
    )
    for tooth in TEETH:
        root_at = offset(at, s * tooth[0], BLADE_Y[1], tooth[1])
        tentacle(p, root_at, offset(root_at, -s * 3, 0, 0.6), [0, 0, 0], [0.8, 0], F.bone, 3)
    graft(p, polygon(5, 2.4, [1, 1.6]), [7.6, 8.4], offset(at, -s * 6, 0, -4), {"color": M.base})


def _draw_core(p: Any) -> None:
    """Draw the core: abdomen and wings, thorax and neck, legs, and lights."""
    _draw_abdomen(p)
    _draw_thorax(p)
    _draw_legs(p)
    lamps(p.neon, [[6, WING_Y[2], -48], [-6.5, WING_Y[2], -14]], 1, GREEN)


def build_mantis_lancer(scene: Any) -> Any:
    """MB-MANTIS-LANCER-01, MB-MANTIS-LANCER-04: the Mantis Lancer.

    A tall, narrow praying mantis with green veins: folded leaf wings over its long abdomen, a
    plated thorax, a long neck to a triangular head, and two scythes raised forward either side.
    """
    return build_boss_model(
        MANTIS_LANCER,
        scene,
        GREEN,
        {
            "core": _draw_core,
            "parts": {"scythe-left": _scythe, "scythe-right": _scythe, "head": _head},
            "armour": {
                "thorax": {"whole": _draw_plating},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
