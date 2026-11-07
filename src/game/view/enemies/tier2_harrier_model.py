# Copyright (c) 2026 Renaud Guillon
"""ENM-HARRIER-01: the Harrier, Cyber-Organic (ENM-35), a tier 2 kind.

A bulky gunship: a wide, squat flesh hull under an armour plate, a heavy pod on each shoulder
carrying a missile launcher, short thick wings and two big reactors. Logical pixels, nose +Z, Y up
(towards the camera).
"""

import math

from game.config.enemy_harrier import HARRIER_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import LOBE_SECTION, SIDES, angry_eyes, decal, flip_x
from game.view.enemies.weapon_ports import port_radius
from render.geometry.organic import SegmentedBody, curve, segmented_body
from render.geometry.organic import vein as vein_tube
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
QUARTER = math.pi / 2

# ENM-HARRIER-01: its wide, squat body (tail to nose) and the armour plate on its back.
HARRIER_BODY = SegmentedBody(-13, 12, 2, 6, -2.4, 3.6)
HARRIER_ARMOUR = [  # type: list[list[float]]
    [0, 11],
    [4.5, 8],
    [5, -6],
    [3, -12],
    [-3, -12],
    [-5, -6],
    [-4.5, 8],
]
# The right shoulder pod (`[x, z]`), and the stub wing out of its back with its edge light.
HARRIER_POD = [[4, 3], [11.5, 3], [12.5, 0], [12.5, -8], [11, -10], [4, -10]]  # type: list[list[float]]
HARRIER_WING = [[12, -2], [16, -6], [16, -9.5], [11.5, -9.5]]  # type: list[list[float]]
HARRIER_WING_LIGHT = [[12.6, -2.6], [15.6, -5.6], [15.2, -6], [12.4, -3.4]]  # type: list[list[float]]
# ENM-HARRIER-02: a launcher's length, from its mouth (the config's muzzle) back onto its pod.
HARRIER_LAUNCHER = 10


def build_harrier(scene: Any) -> Any:
    """ENM-HARRIER-01: a bulky gunship, the missile launcher of tier 2.

    A wide flesh hull under a metal armour plate with angry eyes, a heavy shoulder pod on each
    side with short thick wings and a lime light on their leading edge, two big reactors
    (ENM-HARRIER-04).
    Each pod carries a launcher as the Rocketeer's (ENM-HARRIER-02, ENM-HARRIER-03, WPN-07): a dark
    hexagonal tube hollow down to its floor, the rocket seen in it, lit along its sides, nothing
    glowing at its mouth; lime neon (ENM-HARRIER-04).
    """
    missile = HARRIER_CONFIG.missile.radius
    tube = port_radius(missile)

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        segmented_body(flesh, HARRIER_BODY, F.slate, None, LOBE_SECTION)
        hull.bevel_slab(HARRIER_ARMOUR, [2.4, 2.4, 4.2], [0, 1.2], H.panel, None, H.base)
        for eye in angry_eyes([0, 7.5], 0.8, [2.4, 0.6], 0.4):
            decal(neon, eye, 4.22, N.harrier)
        for s in SIDES:
            pod = HARRIER_POD if s > 0 else flip_x(HARRIER_POD)
            hull.bevel_slab(pod, [-2.6, 0, 2.2], [0.4, 0.8], H.base, None, H.panel)
            wing = HARRIER_WING if s > 0 else flip_x(HARRIER_WING)
            light = HARRIER_WING_LIGHT if s > 0 else flip_x(HARRIER_WING_LIGHT)
            hull.bevel_slab(wing, [-0.8, 0, 0.9], [0.2, 0.4], H.base, None, H.panel)
            decal(neon, light, 0.95, N.harrier)
            # A lime vein from the reactor along the armour's flank.
            vein_tube(
                p.vein,
                curve([s * 4.6, 2.6, -10], [s * 4.6, 2.8, 4], [s * 0.4, 0.3, 0], 3),
                0.45,
                N.harrier,
            )
            # The launcher is its port all along (WPN-07), as the Rocketeer's: a dark hexagonal
            # tube hollow to its floor, drawn bare, a highlight line along each side edge.
            m = HARRIER_CONFIG.muzzles[0 if s > 0 else 1]
            x = s * abs(m[0])
            mouth = -m[1]
            height = m[2]
            for side in [-1, 1]:
                edge = Placement([x + side * tube, height, mouth - HARRIER_LAUNCHER / 2])
                neon.box([0.3, 0.3, HARRIER_LAUNCHER - 0.4], N.harrier, edge)
            # The model's +X is the screen's left: the config's first launcher (WPN-07's 0).
            p.muzzle(
                [x, height, mouth],
                "missile",
                "forward",
                missile,
                0 if s > 0 else 1,
                False,
                HARRIER_LAUNCHER,
            )
            p.reactor([s * 3.2, 0.2, -13.5], 1.6)

    return build_enemy_model("harrier", scene, N.harrier, draw)
