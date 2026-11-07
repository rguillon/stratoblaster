# Copyright (c) 2026 Renaud Guillon
"""FB-SIEGE-CRAWLER-01 to FB-SIEGE-CRAWLER-05: the Siege Crawler, the Lab's L-4 final boss.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A very wide, flat,
low crawler, like a giant trilobite plated as a tank: a head shield with its cannon at the front, a
thorax of overlapping shingle plates either side of a raised axial ridge, a tail shield, and rows of
legs under armoured fenders along both flanks. Its parts and armour are in `siege_crawler_parts`;
its gun mounts are drawn by `build_boss_model` (BOSS-58).
"""

from game.config.bosses.lab.siege_crawler import SIEGE_CRAWLER
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.siege_crawler_parts import (
    BELLY_TOP,
    CHEEK_TOP,
    FLAK_SEAT,
    PLEURA_TOP,
    RED,
    ROTOR_SEAT,
    crawler_armour,
    draw_cannon,
    draw_legs,
    draw_missiles,
    draw_mortar,
)
from game.view.bosses.mini_boss_greebles import lamps, vent
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    gland,
    graft,
    mantle,
    polygon,
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


# Its belly seen from above: wide and short, rounded at the head, tapering to the tail.
BELLY = [
    [0, 44],
    [30, 41],
    [52, 34],
    [62, 22],
    [62, -24],
    [50, -32],
    [30, -38],
    [0, -40],
    [-30, -38],
    [-50, -32],
    [-62, -24],
    [-62, 22],
    [-52, 34],
    [-30, 41],
]
# The head shield's right half, out to its genal spine (mirrored).
CEPHALON = [[0, 43], [26, 41], [48, 35], [58, 26], [60, 16], [0, 16]]
# The thorax's shingle plates: their front edge, from the head shield back to the tail shield.
SHINGLES = [16, 8, 0, -8, -16]
# The tail shield's right half (mirrored).
PYGIDIUM = [[0, -18], [40, -18], [36, -28], [24, -36], [0, -40]]


def _draw_shell(p: Any) -> None:
    """Draw the shell (FB-SIEGE-CRAWLER-02): a wide, flat trilobite's, plated like a tank.

    The belly under it all, rimmed with red; the head shield with its raised ridge; the thorax's
    shingle plates either side of the axial ridge; the tail shield, ribbed.
    """
    mantle(p, BELLY, [-3, BELLY_TOP], F.graphite, RED)
    for s in SIDES:
        head = [[s * q[0], q[1]] for q in CEPHALON]
        p.hull.bevel_slab(head, [1, CHEEK_TOP - 0.8, CHEEK_TOP], [0, 1], M.base, None, M.dark)
        tail = [[s * q[0], q[1]] for q in PYGIDIUM]
        p.flesh.bevel_slab(tail, [1, 4.6, 5.8], [0, 1.2], F.slate, None, F.membrane)
        for z in [-24, -31]:
            p.hull.box([30, 0.6, 1.2], M.dark, Placement([s * 17, 5.6, z], s * 0.12))
    for k in range(len(SHINGLES)):
        front = SHINGLES[k]
        plate = [[-57, front], [57, front], [58, front - 9], [-58, front - 9]]
        color = F.slate if k % 2 == 0 else F.graphite
        y = PLEURA_TOP - 0.25 * k
        p.flesh.bevel_slab(plate, [1, y - 1, y], [0, 1.1], color, None, F.membrane)
        p.neon.box([88, 0.3, 0.5], RED, Placement([0, y - 1.2, front - 9.1]))
    # The glabella: the head shield's raised ridge, the cannon's mantlet standing on it.
    carapace(p.flesh, SegmentedBody(14, 44, 1, 15, 1, 7.5, 0.1), [F.slate, F.membrane])


def _draw_ridge(p: Any) -> None:
    """Draw the axial ridge down its back (FB-SIEGE-CRAWLER-02), the core's guns on it.

    A raised, segmented flesh ridge, grafted seats for the keep gun and the rotor's hatch, the
    tail shield's seat for the flak hatch, and a red vein down it.
    """
    segmented_body(p.flesh, SegmentedBody(-34, 18, 5, 10, 0, 10.2, 0.18), F.sinew)
    carapace(p.flesh, SegmentedBody(-33, 17, 5, 8.6, 6, 10.4, 0.18), [M.panel, F.membrane])
    graft(p, polygon(6, 6.2), [9.8, 11], [0, 0, 9], {"color": M.base})
    graft(p, polygon(8, 7.5), [8.6, ROTOR_SEAT + 0.4], [0, 0, -10], {"color": M.base})
    graft(p, polygon(8, 8.5), [5.4, FLAK_SEAT + 0.4], [0, 0, -27], {"color": M.base})
    spine(p, [0, 10.6, 15], [0, 10.6, 2], {"color": RED, "width": 0.9, "bow": 0.5})
    spine(p, [0, 10.4, -18], [0, 9.4, -34], {"color": RED, "width": 0.9, "bow": 0.5})


def _draw_head(p: Any) -> None:
    """Draw its face (FB-SIEGE-CRAWLER-02): crescent eyes on the head shield, mandibles under it.

    Genal spines sweep back from the shield's corners.
    """
    for s in SIDES:
        p.flesh.cylinder(4, 2, 6, F.graphite, Placement([s * 15, 5, 36]))
        eyes(p, [s * 15, 6.6, 36], {"count": 3, "size": 1.1, "spacing": 2.2}, RED)
        tentacle(p, [s * 58, 2.5, 22], [s * 70, 1, -2], [s * 4, 1, 0], [3, 0.2], F.bone, 4)
        tentacle(p, [s * 7, 1.5, 41], [s * 3, 1, 50], [s * 3, 0, 0], [2.4, 0.1], F.bone, 4)
        # Its feelers, sweeping out forward from under the head shield.
        tentacle(p, [s * 10, 2, 42], [s * 34, 3, 58], [s * -4, 2, 6], [1, 0.15], F.sinew, 4)
    barbs(p, [0, 4, 43], {"count": 5, "spacing": 5, "size": 2.5, "dir": [0, 0.2, 1]})


def _draw_grafts(p: Any) -> None:
    """Grafts and lights (BOSS-49): vents, reactor sacs at the tail, glands, running lights.

    Some details are off the centre line (BOSS-47): a patch and a vent on one side only.
    """
    for s in SIDES:
        reactor_sac(p, [s * 14, 1, -38], 3.2, RED)
        gland(p, [s * 46, PLEURA_TOP - 0.5, 8], 1.5, RED)
        vein_line(p, [s * 11, 6, 4], [s * 46, PLEURA_TOP, 8], [0, 1, 0], 0.8, RED)
        lamps(p.neon, [[s * 56, PLEURA_TOP - 0.3, -14]], 1.2, RED)
    vent(p.hull, [-44, PLEURA_TOP - 0.2, -10], [8, 5], 3, 0.1)
    graft(p, polygon(5, 4, [1.4, 0.9]), [PLEURA_TOP - 0.6, PLEURA_TOP + 0.4], [46, 0, -8])
    p.hull.cylinder(1, 6, 4, M.dark, Placement([30, 5.6, -30]), 0.5)
    p.neon.box([1, 1, 1], RED, Placement([30, 11.6, -30]))


def _draw_core(p: Any) -> None:
    """Draw the core: shell, ridge, face, legs and grafts."""
    _draw_shell(p)
    _draw_ridge(p)
    _draw_head(p)
    draw_legs(p)
    _draw_grafts(p)


def build_siege_crawler(scene: Any) -> Any:
    """FB-SIEGE-CRAWLER-01, FB-SIEGE-CRAWLER-04: the Siege Crawler.

    A very wide, flat, armoured trilobite with red veins: its cannon on the head shield, two mortars
    on its flanks and two missile sponsons behind them, rows of legs along both flanks.
    """
    return build_boss_model(
        SIEGE_CRAWLER,
        scene,
        RED,
        {
            "core": _draw_core,
            "parts": {
                "cannon": draw_cannon,
                "mortar-left": draw_mortar,
                "mortar-right": draw_mortar,
                "missile-left": draw_missiles,
                "missile-right": draw_missiles,
            },
            "armour": crawler_armour(),
        },
    )
