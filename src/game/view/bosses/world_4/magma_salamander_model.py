# Copyright (c) 2026 Renaud Guillon
"""MB-MAGMA-SALAMANDER-01 to MB-MAGMA-SALAMANDER-06, 4-3: the Magma Salamander.

Logical pixels, nose +Z, Y up (towards the camera). A segmented lizard-ship: a flat, wedge-shaped
head, a body of overlapping armour plates with magma glowing in the seams between them (the three
over its back the plating it sheds, MB-MAGMA-SALAMANDER-13), four clawed legs splayed out, a spiny
fin on each side of its back (its parts) and a tail curling back to its right (on two joints).
MB-MAGMA-SALAMANDER-02: a living lizard, its scorched flesh body under bony scale plates and metal
grafts, magma glands along its spine, its reactors set in flesh sacs.
"""

import math

from game.config.bosses.world_4.magma_salamander import (
    MAGMA_SALAMANDER,
    SALAMANDER_JAWS,
    SALAMANDER_VENT,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset, socket
from game.view.bosses.world_3.toucan_jungle import segment
from game.view.bosses.world_4.living_forge import (
    SKIN,
    back_ribs,
    glands,
    lumps,
    magma_vein,
    reactor_sacs,
)
from game.view.bosses.world_4.magma_salamander_armour import (
    BELLY_FLAT,
    PLATES,
    SHED_PLATES,
    draw_plating,
    plate_colour,
    plate_seam,
    plate_stations,
)
from game.view.bosses.world_4.magma_salamander_parts import (
    MOLTEN,
    SALAMANDER_NEON,
    SCORCH,
    barrel,
    fin,
    molten_seam,
    tail,
    tail_limbs,
)
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, HULL_SECTION, SIDES
from render.geometry.organic import RibSpec
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[float]
# __pragma__ ("noskip")


# The underbody along the centre line, tail to neck (loft stations: z, half width, bottom, top),
# flattened to `BELLY_FLAT` under the back plating it sheds (MB-MAGMA-SALAMANDER-13).
BELLY = [
    [-26.0, 6.0, 0.0, BELLY_FLAT],
    [-12.0, 12.0, -1.0, BELLY_FLAT],
    [8.0, 13.0, -1.0, BELLY_FLAT],
    [26.0, 10.0, 0.0, 9.5],
    [36.0, 7.0, 1.0, 8.0],
]
# The head: a flat wedge, from its neck to its snout.
HEAD = [
    [34.0, 8.0, 0.0, 9.0],
    [44.0, 10.5, -0.5, 9.0],
    [54.0, 8.5, 0.0, 7.0],
    [60.0, 5.5, 0.5, 5.0],
    [64.0, 2.0, 1.0, 3.0],
]
# Where its legs leave the body (z, front ones first) and which way their feet point.
LEGS = [
    [22.0, 7.0],
    [-8.0, -7.0],
]


def _draw_body(p: Any) -> None:
    """Draw the underbody, flattened under its back plating (`draw_plating`), and its neck plates.

    A molten seam glows between each plate and the one behind it; its ribs arch over the belly.
    """
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    flesh.loft(HULL_SECTION, BELLY, SKIN.base)
    last = len(PLATES) - 1
    for i in range(SHED_PLATES, len(PLATES)):
        b = hull if i == last else flesh
        b.loft(FIGHTER_SECTION, plate_stations(i), plate_colour(i), None, None)
        plate_seam(neon, i)
    # A scorch mark on the neck plate, lying on its slope (BOSS-52).
    hull.box([4, 0.5, 6], SCORCH, Placement([-4.5, 10.4, 19]))
    glands(
        p,
        [
            [-3, 11.6, 17],
            [0, 10.6, 29],
        ],
        1.6,
        MOLTEN,
    )
    back_ribs(p, [-22, -12, 0, 13], RibSpec(12, 3, 9, 0.8))


def _draw_head(p: Any) -> None:
    """Draw the head: a flat wedge with orange eyes, the jaw guns either side of the snout."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    p.flesh.loft(FIGHTER_SECTION, HEAD, SKIN.base)
    lumps(p, [[0, 6.5, 44]], 4, SKIN.panel, 0.5)
    hull.box([12, 1.6, 12], H.dark, Placement([0, -0.6, 54]))
    molten_seam(neon, [12, 7.6, 37])
    for s in SIDES:
        neon.box([3, 1, 4], SALAMANDER_NEON, Placement([s * 7.2, 7.6, 47], s * 0.4))
        charge.box([1.4, 0.4, 1.8], WHITE, Placement([s * 7.2, 8.6, 47], s * 0.4))
        hull.box([1.4, 2, 9], SHADE["edge"], Placement([s * 9, 7, 42], s * 0.2))
    for m in SALAMANDER_JAWS:
        tip = boss_point(m[0], m[1], m[2])
        hull.box([3, 3, 6], H.panel, Placement(offset(tip, 0, -1.5, -9)), SHADE["edge"])
        barrel(p, tip, [1, 5.5])


def _draw_legs(p: Any) -> None:
    """Four clawed legs splayed out from its sides, armoured at the shoulder."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    for s in SIDES:
        for leg in LEGS:
            z = leg[0]
            reach = leg[1]
            hip = [s * 11, 3, z]
            knee = [s * 21, 5, z + reach * 0.4]
            foot = [s * 27, 0, z + reach]
            segment(flesh, [hip, knee], [3, 2.4], SKIN.panel, 5)
            segment(flesh, [knee, foot], [2.2, 1.4], SKIN.base, 5)
            hull.cylinder(3.2, 2.4, 6, H.dark, Placement(offset(knee, 0, -1.2, 0)))
            neon.box([1, 0.6, 1], MOLTEN, Placement(offset(knee, 0, 1.6, 0)))
            for yaw in [-0.5, 0, 0.5]:
                toe = _sign(reach) * 3.4
                flesh.box(
                    [0.9, 0.9, 3.4],
                    SKIN.bone,
                    Placement(offset(foot, math.sin(yaw) * toe, -0.4, math.cos(yaw) * toe), yaw),
                )


def _sign(v: float) -> float:
    """`Math.sign`."""
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def _draw_back(p: Any) -> None:
    """Draw the fins' sockets on its back, the magma vent between them, and its reactors.

    The vent's stack stands on the flattened belly and rises through the back plating.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    for s in SIDES:
        socket(hull, [s * 14, 3, -4], 4, 6)
    reactor_sacs(
        p,
        [
            [6, 3, -25],
            [-6, 3, -25],
        ],
        2.2,
        MOLTEN,
    )
    # The spine's vein over the neck plates (its length over the back plating is on the plating).
    magma_vein(
        p,
        [
            [0, 11, 13],
            [0, 12, 18],
            [0, 10.5, 30],
        ],
        1,
    )
    if len(SALAMANDER_VENT) == 0:
        return
    m = SALAMANDER_VENT[0]
    top = boss_point(m[0], m[1], m[2])
    # The vent's stack rises from the flattened belly, through the back plating (BOSS-52).
    foot = BELLY_FLAT - 0.2
    hull.cylinder(5.4, top[1] - 0.4 - foot, 7, SCORCH, Placement([top[0], foot, top[2]]), 3.4)
    neon.ring(3.6, 0.6, 7, MOLTEN, Placement(offset(top, 0, -1.2, 0)))
    charge.cylinder(2.8, 0.6, 7, WHITE, Placement(offset(top, 0, -0.6, 0)))
    muzzle(top, "ring")
    hull.box([2, 1, 6], H.dark, Placement(offset(top, 0, -4, 6), 0, QUARTER / 8))


def build_magma_salamander(scene: Any) -> Any:
    """MB-MAGMA-SALAMANDER-01, MB-MAGMA-SALAMANDER-05: the Magma Salamander.

    A segmented lizard-ship with a molten glow between its plates, orange-yellow neon, spiny back
    fins and a lashing tail.
    """

    def core(p: Any) -> None:
        _draw_body(p)
        _draw_head(p)
        _draw_legs(p)
        _draw_back(p)

    return build_boss_model(
        MAGMA_SALAMANDER,
        scene,
        SALAMANDER_NEON,
        {
            "core": core,
            "parts": {"fin-left": fin, "fin-right": fin, "tail": tail},
            "limbs": tail_limbs(),
            "armour": {"back": {"whole": draw_plating}},
        },
    )
