# Copyright (c) 2026 Renaud Guillon
"""ENM-HARRIER-01: the Harrier, Cyber-Organic (ENM-35), a tier 2 kind.

A sleek swept dart: a slim flesh fuselage, metal wings and twin missile rails. Logical pixels, nose
+Z, Y up (towards the camera).
"""

import math

from game.config.enemy_harrier import HARRIER_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.basic_parts import eye_pair
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import LOBE_SECTION, SIDES, decal, flip_x
from game.view.enemies.organic_parts import reactor_sac
from game.view.enemies.weapon_ports import port_depth, port_radius
from render.geometry.organic import (
    SegmentedBody,
    curve,
    segmented_body,
    tendril,
)
from render.geometry.organic import (
    vein as vein_tube,
)
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2

# ENM-HARRIER-01: the right wing, swept back from the fuselage (x, z).
HARRIER_WING = [[1.5, 5], [14, -10], [14, -12.5], [1.5, -8]]  # type: list[list[float]]
# The neon light along the wing's leading edge.
HARRIER_WING_LIGHT = [[3.6, 3.2], [13, -9.4], [12.5, -10.2], [3, 2.4]]  # type: list[list[float]]
# ENM-HARRIER-02: a rail's length, from its back to its tip, and where its back is (Z).
RAIL_LENGTH = 12
RAIL_BACK = -3
RAIL_HEIGHT = -1.4
# A rail is a hexagonal tube as wide as its port, which is wider than its rocket (WPN-07).
RAIL_RADIUS = port_radius(HARRIER_CONFIG.missile.radius)


def build_harrier(scene: Any) -> Any:
    """ENM-HARRIER-01: a swept dart, the missile launcher of tier 2.

    A slim flesh fuselage with a metal spike on its nose, swept metal wings with a neon edge, one
    reactor in a flesh sac (ENM-HARRIER-04); twin missile rails under the wings, charge lights at
    their tips (ENM-HARRIER-02, ENM-HARRIER-03); lime neon (ENM-HARRIER-04).
    """
    rail_x = HARRIER_CONFIG.muzzles[1][0]

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        body = SegmentedBody(-12, 15, 2, 2.6, -1.2, 2.3)
        segmented_body(flesh, body, F.slate, None, LOBE_SECTION)
        hull.cylinder(1, 4, 5, H.panel, Placement([0, 0.4, 12.6], 0, QUARTER), 0)
        eye_pair(p, [0, 1.6, 8], 0.9, 0.45, N.harrier)
        vein_tube(p.vein, curve([0, 2.3, -9], [0, 2.4, 4], [0, 0.6, 0], 3), 0.5, N.harrier)
        for s in SIDES:
            wing = HARRIER_WING if s > 0 else flip_x(HARRIER_WING)
            light = HARRIER_WING_LIGHT if s > 0 else flip_x(HARRIER_WING_LIGHT)
            hull.bevel_slab(wing, [-0.4, 0, 0.5], [0.2, 0.3], H.base, None, H.panel)
            decal(neon, light, 0.55, N.harrier)
            # The strut that holds the rail under the wing, and the rail itself.
            tendril(
                flesh,
                curve([s * 3, 0, 0], [s * rail_x, RAIL_HEIGHT, 0], [0, 0, 0], 2),
                [1, 0.7],
                3,
                F.sinew,
            )
            # The launcher: a hexagonal tube as wide as its port (WPN-07), its hole at the tip,
            # glowing as the next missile is ready.
            tip = RAIL_BACK + RAIL_LENGTH
            # The rail stops where its port's well starts, so nothing closes the hole.
            well = port_depth(HARRIER_CONFIG.missile.radius)
            hull.cylinder(
                RAIL_RADIUS,
                tip + 0.6 - well - RAIL_BACK,
                6,
                H.dark,
                Placement([s * rail_x, RAIL_HEIGHT, RAIL_BACK], 0, QUARTER),
            )
            # The model's +X is the screen's left: the config's first rail (WPN-07's launcher 0).
            p.muzzle(
                [s * rail_x, RAIL_HEIGHT, tip + 0.6],
                "missile",
                "forward",
                HARRIER_CONFIG.missile.radius,
                0 if s > 0 else 1,
            )
        reactor_sac(p, [0, 0.1, -12], 1.4, N.harrier, F.sinew, 3)

    return build_enemy_model("harrier", scene, N.harrier, draw)
