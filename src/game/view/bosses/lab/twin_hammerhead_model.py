# Copyright (c) 2026 Renaud Guillon
"""MB-TWIN-HAMMERHEAD-01 to MB-TWIN-HAMMERHEAD-05, Lab L-2: the Twin Hammerhead.

Logical pixels, nose +Z, Y up (towards the camera). A catamaran of two hammerhead sharks side by
side, wide apart, joined by a bony bridge carrying the core; a cannon on each hammer head, a
missile block on the bridge's rear hump, armour plates on the bridge (shed at its transformation).
Lab boss: in the dev viewer only.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.twin_hammerhead import (
    BRIDGE_PLATE,
    BRIDGE_TOP,
    HULL_X,
    TWIN_HAMMERHEAD,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_greebles import lamps, mast
from game.view.bosses.mini_boss_shapes import offset
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    gland,
    graft,
    growth,
    hide,
    polygon,
    sac,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["twin-hammerhead"]

# A hammer head seen from above, around its hull's centre line (x across, z along, nose +Z): a wide
# flat blade, its front edge bowed forward, its back swept in to the neck.
HAMMER = [
    [-19, 29],
    [-17, 34],
    [-8, 37],
    [0, 38],
    [8, 37],
    [17, 34],
    [19, 29],
    [17, 25.5],
    [8, 24.5],
    [4, 20],
    [-4, 20],
    [-8, 24.5],
    [-17, 25.5],
]
# Heights of a hammer head: its underside, its edge, its top.
HAMMER_Y = [-1.5, 2.5, 6]
# A pectoral fin, on the outer flank of its hull (x outwards from the hull's centre line).
FIN = [[6, 12], [19, -3], [21, -10], [14, -7], [6, 2]]
# The tail fin, forked, its outer lobe the longer (x outwards from the hull's centre line).
TAIL = [[0, -42], [4, -50], [11, -62], [3, -56], [0, -53], [-3, -56], [-7, -59], [-4, -50]]
# The bridge between the hulls seen from above: its front lip at +Z, its rear under the hump.
BRIDGE = [
    [-31, 15],
    [-18, 12.5],
    [-7, 14],
    [0, 17],
    [7, 14],
    [18, 12.5],
    [31, 15],
    [31, -24],
    [20, -21],
    [10, -27],
    [0, -29.5],
    [-10, -27],
    [-20, -21],
    [-31, -24],
]
# A bridge plate, a rounded bony scute, around its centre (x outwards, z along): it lies within
# the armour region of the design (`BRIDGE_PLATE`).
SCUTE = [  # type: list[Any]
    [-8, 7.5],
    [-4, 10],
    [4, 10],
    [8, 7.5],
    [8.5, -8.5],
    [4, -10.5],
    [-4, -10.5],
    [-8.5, -8.5],
]
# The core's dome on the bridge: its centre (model space), radius and height.
DOME = [0, 4, -4]  # type: list[Any]
DOME_R = 8.5


def _moved(outline: list[Any], dx: float, side: float = 1) -> list[Any]:
    """Return an outline around a hull's centre line, mirrored by `side`, moved `dx` across."""
    return [[dx + side * q[0], q[1]] for q in outline]


def _draw_hull(p: Any, s: float) -> None:
    """Draw one shark hull (MB-TWIN-HAMMERHEAD-02), at model x `s * HULL_X`.

    Its body along Z under a plated carapace, the hammer head across its nose with an eye at each
    tip and teeth under its front edge, a dorsal fin, a pectoral fin on its outer flank, its forked
    tail, gill slits and a vein along its spine.
    """
    hx = s * HULL_X
    hide(
        p,
        {
            "at": [hx, 0, 0],
            "tail": -48,
            "nose": 24,
            "width": 9.5,
            "bottom": -4,
            "top": 10.5,
            "segments": 3,
            "shell": [F.slate, F.membrane],
            "belly": F.graphite,
        },
    )
    p.flesh.bevel_slab(_moved(HAMMER, hx), HAMMER_Y, [1, 1.5], F.slate, None, F.graphite)
    p.flesh.bevel_slab(_moved(FIN, hx, s), [-1, 0.2, 1.4], [0.4, 0.8], F.slate)
    p.flesh.bevel_slab(_moved(TAIL, hx, s), [0, 1, 2.2], [0.3, 0.6], F.slate)
    fin = [[hx, 9.5, 9], [hx, 24, -9], [hx, 21.5, -10], [hx, 9.5, -7]]
    p.flesh.face(fin, F.slate)
    p.flesh.face([fin[3], fin[2], fin[1], fin[0]], F.slate)
    spine(p, [hx, 10.6, -36], [hx, 10.8, 18], {"color": N, "width": 1.1, "bow": 1})
    for t in SIDES:
        tip = [hx + t * 17.5, 3.6, 30]
        p.hull.cylinder(2.3, 1.4, 6, M.dark, Placement(offset(tip, 0, -0.6, 0)))
        eyes(p, tip, {"count": 1, "size": 1.5}, N)
        for z in [15, 12, 9]:
            vein_line(p, [hx + t * 6.6, 5.5, z], [hx + t * 7.4, 2, z - 1.5], [0, 0, 0], 0.7, N)
    barbs(p, [hx, 0.5, 36], {"count": 5, "spacing": 3.2, "size": 2.6, "dir": [0, -0.3, 1]})
    # Grafts on its back: two riveted plates and an armour band.
    graft(p, polygon(4, 4, [0.9, 2]), [10, 11.2], [hx, 0, -20], {"color": M.base})
    graft(p, polygon(6, 3.2), [10.2, 11.2], [hx, 0, 13])
    p.hull.box([19.5, 1.6, 2.2], M.dark, Placement([hx, 7.8, -28]), M.panel)


def _draw_bridge(p: Any) -> None:
    """Draw the bony bridge (MB-TWIN-HAMMERHEAD-02): a sinew deck between the hulls.

    Two bone beams across (its front lip under the bridge turret, its rear under the hump), the
    core's dome in its middle with a vein ring round its foot, veins out to the hulls, a gland and
    its reactors.
    """
    p.flesh.bevel_slab(BRIDGE, [0.5, 2.5, BRIDGE_TOP], [1.2, 1.5], F.membrane, None, F.graphite)
    for z, y, r in [[13.5, 3.4, 2.2], [-22, 3, 2.5]]:
        tentacle(p, [-31, y, z], [31, y, z], [0, 0.01, 0], [r, r], F.bone, 5)
        for x in [-24, -12, 12, 24]:
            organ(p.flesh, r * 1.45, 5, F.bone, Placement([x, y - r * 1.2, z]), 0.85)
    for s in SIDES:
        # Bone ribs along the hulls' inner flanks, from the front beam to the rear one.
        tentacle(p, [s * 29, 3.5, 13], [s * 29, 3.5, -21], [s * -3, 3, 0], [1.8, 1.8], F.bone, 4)
    # The bridge turret's seat on the front lip (its mount, BOSS-58).
    graft(p, polygon(6, 4.6), [BRIDGE_TOP - 0.6, BRIDGE_TOP + 0.6], [0, 0, 13], {"color": M.base})
    organ(p.flesh, DOME_R, 8, F.slate, Placement(DOME, math.pi / 8), 0.47)
    p.vein.ring(DOME_R * 0.92, 0.5, 8, N, Placement([0, 6.2, DOME[2]], math.pi / 8))
    for s in SIDES:
        vein_line(p, [s * 7, 6, -16], [s * 28, 5.5, -18], [0, 1.5, 0], 1, N)
        vein_line(p, [s * 7, 5.4, 10], [s * 28, 5, 10.5], [0, 1, 0], 0.9, N)
        reactor_sac(p, [s * 18, 2.6, -24], 2.8, N)
    gland(p, [-13, BRIDGE_TOP, 11], 1.3, N)
    lamps(p.neon, [[s * 33, BRIDGE_TOP, 15] for s in SIDES], 1.1, N)


def _draw_plates(p: Any) -> None:
    """Draw the bridge's armour plates (MB-TWIN-HAMMERHEAD-05): the armour it sheds.

    A bony scute either side of the dome, a riveted plate on each, a vein across it and a gland
    over the gatling folded under it.
    """
    cx = (BRIDGE_PLATE[0][0] + BRIDGE_PLATE[1][0]) / 2
    cz = -(BRIDGE_PLATE[0][1] + BRIDGE_PLATE[2][1]) / 2
    for s in SIDES:
        at = [s * cx, 0, cz]
        scute = [[q[0], q[1] + cz] for q in SCUTE]
        p.flesh.bevel_slab(_moved(scute, at[0]), [BRIDGE_TOP, 7.6, 9.6], [0.4, 2], F.bone)
        p.flesh.bevel_slab(
            _moved([[q[0] * 0.55, q[1] * 0.6 + cz] for q in SCUTE], at[0]),
            [9.4, 10.2, 11],
            [0, 0.8],
            F.sinew,
        )
        for dx in [-5.5, 5.5]:
            tentacle(
                p,
                [at[0] + dx, 9.3, cz + 8],
                [at[0] + dx, 9.3, cz - 8],
                [0, 1, 0],
                [1, 1],
                F.bone,
                4,
            )
        vein_line(
            p, [at[0] - s * 7.5, 9.6, cz + 6], [at[0] - s * 7.5, 9.6, cz - 7], [0, 0.6, 0], 0.9, N
        )
        gland(p, [at[0] + s * 5.5, 9.4, cz - 9.5], 1.1, N)


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the bridge rotor (BOSS-58): an armoured cap on the dome, a seam of light.

    It bursts off as the rotor comes into use.
    """
    turn = math.pi / 8
    p.hull.cylinder(6.2, 1.6, 8, M.panel, Placement([0, 10.8, DOME[2]], turn), 5.6)
    p.hull.cylinder(3.8, 1.2, 8, M.base, Placement([0, 12.4, DOME[2]], turn), 3)
    p.neon.ring(6, 0.3, 8, N, Placement([0, 11.9, DOME[2]], turn))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    p.hull.ring(5.8, 1.4, 16, M.base, Placement([0, 10.8, DOME[2]]))
    p.neon.ring(5.8, 0.3, 16, N, Placement([0, 12, DOME[2]]))


def _cannon(p: Any, at: Vec3) -> None:
    """Add a hammer cannon (MB-TWIN-HAMMERHEAD-03): an armoured growth on the hammer head.

    Under its three-barrelled turret (its mount, BOSS-58), bone spikes behind it, a sac at its side.
    """
    growth(p, offset(at, 0, 4.6, 0), 7.6, N, {"flesh": F.graphite, "height": 0.34})
    barbs(p, offset(at, 0, 6.5, -7), {"count": 3, "spacing": 4, "size": 3, "dir": [0, 0.4, -1]})
    side = 1 if at[0] > 0 else -1
    sac(p, offset(at, side * 9, 5, -3), 2.6, F.slate, {"stretch": 0.6})


def _missile_block(p: Any, at: Vec3) -> None:
    """Add the missile block (MB-TWIN-HAMMERHEAD-03): a bony hump on the bridge's rear.

    A plate grafted on its crown under the block of four missile ports (its mount, BOSS-58), a vein
    ring round its foot.
    """
    organ(p.flesh, 9, 8, F.bone, Placement(offset(at, 0, 3.4, 0), math.pi / 8), 0.34)
    p.vein.ring(8.2, 0.5, 8, N, Placement(offset(at, 0, 4.4, 0), math.pi / 8))
    graft(p, polygon(6, 7.4), [8.8, 9.5], at, {"color": M.base})


def build_twin_hammerhead(scene: Any) -> Any:
    """MB-TWIN-HAMMERHEAD-01, MB-TWIN-HAMMERHEAD-04: the Twin Hammerhead.

    Two hammerhead-shark hulls with red-orange veins, joined by a bony bridge carrying the core's
    dome; a cannon on each hammer head and a missile block on the bridge's rear hump (its parts),
    the bridge turret and the rotor on the dome (the core's mounts, BOSS-58).
    """

    def core(p: Any) -> None:
        for s in SIDES:
            _draw_hull(p, s)
        _draw_bridge(p)
        # A short mast on the right hull only (off the centre line).
        mast(p, [-HULL_X, 9.4, -6], 7, N)

    return build_boss_model(
        TWIN_HAMMERHEAD,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "cannon-left": _cannon,
                "cannon-right": _cannon,
                "missile-block": _missile_block,
            },
            "armour": {
                "bridge": {"whole": _draw_plates},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
