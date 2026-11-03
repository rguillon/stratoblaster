# Copyright (c) 2026 Renaud Guillon
"""FB-STORM-PETREL-01 to FB-STORM-PETREL-04: the Storm Petrel, the final boss of 1-1.

Logical pixels, nose +Z, Y up (towards the camera). A colossal sea-bird creature: a long shelled
body, broad membrane wings on bone struts with an engine sac on each, magenta veins along the wing
edges; its parts are growths on its wings, tail and breast. Its armour (the tail plating, the wing
roots) and its outer wings are drawn as pieces of their own (`storm_petrel_armour`,
`storm_petrel_wings`, D-254).
"""

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.final_bosses import STORM_PETREL
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_petrel import draw_plate, draw_pod, draw_rack
from game.view.bosses.final_boss_shapes import edge_strips, shift, sided, turret
from game.view.bosses.storm_petrel_armour import (
    BOTTOM,
    MID,
    NOSE,
    SEGMENTS,
    TAIL,
    TAIL_Z,
    WIDTH,
    draw_shell,
    petrel_armour,
)
from game.view.bosses.storm_petrel_wings import draw_floats
from game.view.bosses.world_1_organic_kit import F, M, graft, polygon, rib_cage, tentacle
from game.view.enemies.enemy_shapes import SIDES, flip_x
from game.view.enemies.organic_parts import eyes
from render.geometry.organic import SegmentedBody, segmented_body
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["storm-petrel"]

# The right tailplane and the fin standing at its tip (in its own plane, rolled upright).
TAILPLANE = [
    [4, -48],
    [30, -56],
    [31, -62],
    [24, -64],
    [4, -62],
]


def _draw_hull(p: Any) -> None:
    """Draw the body (FB-STORM-PETREL-02): a long shelled body from tail to beak.

    Its belly the whole length, its shell short of the tail plating (the armour, drawn apart), ribs
    across its shoulders, plated grafts on its back, eyes over its beak, a tail light on the tail's
    tip and the barbette of the cockpit turret growing out of its back.
    """
    segmented_body(p.flesh, SegmentedBody(TAIL, NOSE, SEGMENTS, WIDTH, BOTTOM, MID, 0.15), F.slate)
    draw_shell(p.flesh, TAIL, TAIL_Z[0])
    draw_shell(p.flesh, TAIL_Z[1], NOSE)
    rib_cage(p, [-22, -12, 14], {"halfWidth": 15, "y": 3, "height": 12, "thickness": 1.1})
    graft(p, polygon(6, 5, [1.2, 1.6]), [13.6, 15], [0, 0, 26])
    graft(p, polygon(4, 4, [1.4, 1]), [13.6, 14.8], [0, 0, 38], {"color": M.base})
    eyes(p, [0, 9.5, 46], {"count": 2, "size": 1.4, "spacing": 7}, N)
    # A barbette of flesh rising out of the back, the gun turret on it: the cockpit turret.
    p.flesh.cylinder(8.5, 7.5, 7, F.sinew, Placement([0, 7, 5]), 8)
    p.neon.box([2, 1.2, 1], N, Placement([0, 10.4, -60]))


def _cockpit_turret(p: Any, at: Vec3) -> None:
    """Add the cockpit turret on its barbette (the core's gun, FB-STORM-PETREL-03).

    It turns around its pivot `at`.
    """
    turret(p, shift(at, [0, 14.5, 0]), 8.5, [2, N])


def _draw_tail(p: Any) -> None:
    """Draw the tailplanes: membrane on bone, their fins of bone, neon on their leading edges."""
    for s in SIDES:
        plane = TAILPLANE if s > 0 else flip_x(TAILPLANE)  # type: ignore[arg-type]  # the argument does not match the parameter type mypy expects
        p.flesh.bevel_slab(plane, [7, 8, 9.5], [0.6, 1], F.membrane, None, F.graphite)
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
    """FB-STORM-PETREL-01, FB-STORM-PETREL-04: the Storm Petrel.

    A colossal sea-bird creature 4.5 L across its wings, magenta veins along the wing edges; a gun
    growth on each wing, a missile brood on its tail, a bony shell over its breast, and a cockpit
    turret on its back (the core). Its wings and its tail plating are drawn apart as its armour and
    moving pieces (FB-STORM-PETREL-05).
    """

    def core(p: Any) -> None:
        _draw_hull(p)
        draw_floats(p)
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
            "armour": petrel_armour(),
        },
    )
