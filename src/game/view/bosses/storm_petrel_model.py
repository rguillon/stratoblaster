"""P07-R05, P16-R06: the Storm Petrel, the final boss of 1-1 Logical pixels, nose +Z, Y up (towards
the camera). A colossal
sea-bird creature: a long shelled body, broad membrane wings on bone struts with an engine sac on
each, magenta veins along the wing edges; its parts are growths on its wings, tail and breast.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.final_bosses import STORM_PETREL  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_petrel import draw_plate, draw_pod, draw_rack  # noqa: E402
from game.view.bosses.final_boss_shapes import edge_strips, shift, sided, turret  # noqa: E402
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    gland,
    graft,
    hide,
    polygon,
    rib_cage,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES, flip_x  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.organic import SegmentedBody, segmented_body  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

N = BOSS_LOOK.neon["storm-petrel"]

# The right wing, root inside the body, its tip squared off; the gun pod sits near its tip.
WING = [
    [8, 20],
    [36, 12],
    [74, 3],
    [77, -1],
    [76, -7],
    [56, -10],
    [30, -14],
    [8, -20],
]
# Neon along the right wing's leading edge and around its tip, just proud of the edge.
WING_LEAD = [
    [13, 19.4],
    [36, 12.8],
    [74.4, 3.8],
    [77.8, -1],
    [76.8, -7.6],
]
# The bone struts of the right wing, from its root out (x, z of their ends).
STRUTS = [
    [
        [10, 16],
        [74, 2],
    ],
    [
        [10, 4],
        [70, -8],
    ],
    [
        [10, -8],
        [46, -11],
    ],
]
# The right tailplane and the fin standing at its tip (in its own plane, rolled upright).
TAILPLANE = [
    [4, -48],
    [30, -56],
    [31, -62],
    [24, -64],
    [4, -62],
]
NACELLE_X = 24
WING_Y = [6, 7.5, 9.5]


def _draw_hull(p: Any) -> None:
    """The body (P16-R06): a long shelled body from tail to beak, plated grafts on its back, ribs
    across its shoulders, a magenta vein down its spine, eyes over its beak, and the barbette of the
    cockpit turret growing out of its back."""
    hide(
        p,
        {
            "tail": -64,
            "nose": 56,
            "width": 14,
            "bottom": -4,
            "top": 15,
            "segments": 7,
            "shell": [F.purple, F.membrane],
            "belly": F.crimson,
        },
    )
    rib_cage(p, [-22, -12, 14], {"halfWidth": 15, "y": 3, "height": 12, "thickness": 1.1})
    spine(p, [0, 15.5, -50], [0, 15.5, -10], {"color": N, "width": 1.4})
    graft(p, polygon(6, 5, [1.2, 1.6]), [13.6, 15], [0, 0, 26])
    graft(p, polygon(4, 4, [1.4, 1]), [13.6, 14.8], [0, 0, 38], {"color": M.base})
    eyes(p, [0, 9.5, 46], {"count": 2, "size": 1.4, "spacing": 7}, N)
    barbs(p, [0, 14, -32], {"count": 3, "spacing": 0.1, "size": 4, "dir": [0, 1, -0.5]})
    # A barbette of flesh rising out of the back, the gun turret on it: the cockpit turret.
    p.flesh.cylinder(8.5, 7.5, 7, F.sinew, Placement([0, 7, 5]), 8)
    p.neon.box([2, 1.2, 1], N, Placement([0, 4.4, -64.4]))


def _cockpit_turret(p: Any, at: Vec3) -> None:
    """The cockpit turret on its barbette (the core's gun), turning around its pivot `at`."""
    turret(p, shift(at, [0, 14.5, 0]), 8.5, [2, N])


def _draw_wings(p: Any) -> None:
    """Both wings (P16-R06): a membrane on bone struts (big, heavy wings: they stay still), neon
    along their leading edges, veins across them, an engine sac on each with its reactor, a float
    of flesh under each root."""
    for s in SIDES:
        p.flesh.bevel_slab(sided(WING, s), WING_Y, [1.2, 1.8], F.membrane, None, F.purple)
        edge_strips(p.neon, sided(WING_LEAD, s), 1.2, [6.9, 8.1], N)
        for strut in STRUTS:
            start = strut[0]
            end = strut[1]
            tentacle(
                p,
                [s * start[0], 9, start[1]],
                [s * end[0], 9, end[1]],
                [0, 1.2, 0],
                [1.8, 0.5],
                F.bone,
                4,
            )
        vein_line(p, [s * 12, 9.8, -2], [s * 60, 9.7, -6], [0, 0.6, 2], 1.1, N)
        nacelle = [s * NACELLE_X, 7, 0]
        segmented_body(
            p.flesh,
            SegmentedBody(-19, 19, 3, 5.5, -1, 9),
            F.crimson,
            Placement(nacelle),  # type: ignore[arg-type]
        )
        graft(p, polygon(5, 3.4), [9, 10], shift(nacelle, [0, 0, 12]))
        p.neon.ring(3.6, 0.8, 6, N, Placement(shift(nacelle, [0, 3.8, 19.2]), 0, math.pi / 2))
        reactor_sac(p, shift(nacelle, [0, 3.5, -19.2]), 3.2, N)
        segmented_body(
            p.flesh,
            SegmentedBody(-14, 24, 2, 4, 0, 5.5),
            F.sinew,
            Placement([s * 20, -4, 0]),
        )
        gland(p, [s * 76.6, 8.6, -3.5], 1.2, N)


def _draw_tail(p: Any) -> None:
    """The tailplanes: membrane on bone, their fins of bone, neon on their leading edges."""
    for s in SIDES:
        plane = TAILPLANE if s > 0 else flip_x(TAILPLANE)  # type: ignore[arg-type]
        p.flesh.bevel_slab(plane, [7, 8, 9.5], [0.6, 1], F.membrane, None, F.purple)
        tentacle(p, [s * 4, 9, -50], [s * 30, 9, -57], [0, 1, 0], [1.4, 0.4], F.bone, 4)
        tentacle(p, [s * 28, 9, -55], [s * 28, 19, -63], [0, 0, 2], [1.4, 0.2], F.bone, 4)
        edge_strips(
            p.neon,
            sided(
                [
                    [6, -48.6],
                    [30.4, -55.6],
                ],
                s,
            ),
            1,
            [7.6, 8.6],
            N,
        )


def build_storm_petrel(scene: Any) -> Any:
    """P07-R05, P16-R06: the Storm Petrel, a colossal sea-bird creature 4.5 L across its wings,
    magenta veins along the wing edges; a gun growth on each wing, a missile brood on its tail, a
    bony shell over its breast, and a cockpit turret on its back (the core)."""

    def core(p: Any) -> None:
        _draw_hull(p)
        _draw_wings(p)
        _draw_tail(p)

    return build_boss_model(
        STORM_PETREL,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "pod-left": draw_pod,
                "pod-right": draw_pod,
                "missile-rack": draw_rack,
                "belly-plate": draw_plate,
            },
            "turrets": {"core": _cockpit_turret},
        },
    )
