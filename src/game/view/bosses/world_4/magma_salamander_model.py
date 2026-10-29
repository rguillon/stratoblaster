"""P10-R11, 4-3: the Magma Salamander. Ported from `bosses/world-4/magma-salamander-model.ts`.
Logical
pixels, nose +Z, Y up (towards the camera). A segmented lizard-ship: a flat, wedge-shaped head, a
body of overlapping armour plates with magma glowing in the seams between them, four clawed legs
splayed out, a spiny fin on each side of its back (its parts) and a tail curling back to its right
(on two joints). P16-R05: a living lizard, its scorched flesh body under bony scale plates and metal
grafts, magma glands along its spine, its reactors set in flesh sacs.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.magma_salamander import (  # noqa: E402
    MAGMA_SALAMANDER,
    SALAMANDER_JAWS,
    SALAMANDER_VENT,
)
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import vent  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset, socket  # noqa: E402
from game.view.bosses.world_3.toucan_jungle import segment  # noqa: E402
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    SKIN,
    back_ribs,
    glands,
    lumps,
    magma_vein,
    reactor_sacs,
)
from game.view.bosses.world_4.magma_salamander_parts import (  # noqa: E402
    MOLTEN,
    SALAMANDER_NEON,
    SCORCH,
    barrel,
    fin,
    molten_seam,
    tail,
    tail_limbs,
)
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, HULL_SECTION, SIDES  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The underbody along the centre line, tail to neck (loft stations: z, half width, bottom, top).
BELLY = [
    [-26.0, 6.0, 0.0, 6.0],
    [-12.0, 12.0, -1.0, 9.5],
    [8.0, 13.0, -1.0, 10.5],
    [26.0, 10.0, 0.0, 9.5],
    [36.0, 7.0, 1.0, 8.0],
]
# The armour plates over the body, back to front: from and to (z), half width, top.
PLATES = [
    [-26.0, -18.0, 8.0, 8.0],
    [-17.0, -4.0, 13.5, 11.0],
    [-2.0, 10.0, 14.5, 12.0],
    [12.0, 24.0, 13.0, 11.5],
    [26.0, 35.0, 10.0, 10.0],
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
    """The underbody and its plates, a molten seam glowing between each plate and the next."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    flesh.loft(HULL_SECTION, BELLY, SKIN.base)
    last = len(PLATES) - 1
    for i in range(len(PLATES)):
        entry = PLATES[i]
        z0 = entry[0]
        z1 = entry[1]
        half = entry[2]
        top = entry[3]
        plate = [
            [z0, half * 0.85, 1, top - 1.2],
            [z0 + 2, half, 0.5, top],
            [z1 - 2, half, 0.5, top],
            [z1, half * 0.88, 1, top - 1],
        ]
        b = hull if i == last else flesh
        colour = SKIN.dark if i % 2 == 0 else SKIN.panel
        b.loft(FIGHTER_SECTION, plate, colour, None, None)
        if i > 0:
            molten_seam(neon, [half * 1.5, top - 1.6, z0 - 0.5])
    for s in SIDES:
        neon.box([0.6, 0.5, 40], SALAMANDER_NEON, Placement([s * 13.6, 6.2, 4], s * 0.04))
        hull.box([4, 0.5, 6], SCORCH, Placement([s * 6, 11.6, 16 - s * 10]))
    vent(hull, [-6, 12.2, 3], [5, 6], 3)
    glands(
        p,
        [
            [4, 12, -11],
            [-3, 11.6, 17],
            [0, 10.6, 29],
        ],
        1.6,
        MOLTEN,
    )
    back_ribs(p, [-22, -12, 0, 13], RibSpec(12, 3, 9, 0.8))


def _draw_head(p: Any) -> None:
    """The head: a flat wedge with orange eyes, the jaw guns either side of the snout."""
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
    """The fins' sockets on its back, the magma vent between them, and its reactors."""
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
    magma_vein(
        p,
        [
            [0, 9, -20],
            [0, 11, -8],
            [0, 12, 10],
            [0, 10.5, 30],
        ],
        1,
    )
    if len(SALAMANDER_VENT) == 0:
        return
    m = SALAMANDER_VENT[0]
    top = boss_point(m[0], m[1], m[2])
    hull.cylinder(
        5.4,
        top[1] - 10.4,
        7,
        SCORCH,
        Placement(offset(top, 0, -(top[1] - 10), 0)),
        3.4,
    )
    neon.ring(3.6, 0.6, 7, MOLTEN, Placement(offset(top, 0, -1.2, 0)))
    charge.cylinder(2.8, 0.6, 7, WHITE, Placement(offset(top, 0, -0.6, 0)))
    muzzle(top, "ring")
    hull.box([2, 1, 6], H.dark, Placement(offset(top, 0, -4, 6), 0, QUARTER / 8))


def build_magma_salamander(scene: Any) -> Any:
    """P10-R11: the Magma Salamander, a segmented lizard-ship with a molten glow between its plates,
    orange-yellow neon, spiny back fins and a lashing tail."""

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
        },
    )
