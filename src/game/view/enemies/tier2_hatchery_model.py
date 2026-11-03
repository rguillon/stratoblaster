# Copyright (c) 2026 Renaud Guillon
"""ENM-HATCHERY-01: the Hatchery, Cyber-Organic (ENM-35), a tier 2 kind.

An armoured egg pod with a launch hatch under its belly. Logical pixels, nose +Z, Y up (towards the
camera).
"""

import math

from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.enemy_shapes import LOBE_SECTION, SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import (
    SegmentedBody,
    curve,
    segmented_body,
    tendril,
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

# The pod: its tail and nose (Z), and its bottom and top at its widest.
POD_BOTTOM = -4
POD_TOP = 9
# ENM-HATCHERY-01: the armour plates on the back, `[z, top of the pod there, half width, half
# length]`.
HATCHERY_PLATES = [[-18, 6.9, 5.5, 5], [0, 9, 7, 6], [18, 6.9, 5.5, 5]]  # type: list[list[float]]
# The ribs arched over the back, at these Z.
HATCHERY_RIBS = [-9, 9]  # type: list[float]
# A glowing bead of flesh (8 triangles): the charge lamps on the flanks.
LAMP = [[0, -0.7], [1.6, 0], [0, 0.9]]  # type: list[list[float]]


def plate_outline(plate: list[float]) -> list[list[float]]:
    """Return the outline of an armour plate: a hexagon at `[z, _, half width, half length]`."""
    z = plate[0]
    w = plate[2]
    length = plate[3]
    return [
        [-w * 0.7, z - length],
        [w * 0.7, z - length],
        [w, z],
        [w * 0.7, z + length],
        [-w * 0.7, z + length],
        [-w, z],
    ]


def build_hatchery(scene: Any) -> Any:
    """ENM-HATCHERY-01: an armoured egg pod, the carrier of tier 2.

    A swollen flesh egg of three segments under three metal armour plates and two bone ribs, lime
    neon bands on the plates; a launch hatch under its belly with a ring of charge light, and a
    charge lamp on each flank, all brightening as the next launch nears (ENM-HATCHERY-02,
    ENM-HATCHERY-03); two reactors in flesh sacs (ENM-HATCHERY-04); lime neon (ENM-HATCHERY-04).
    """
    hatch_z = -HATCHERY_CONFIG.hatch[1]

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        charge = p.charge
        segmented_body(
            flesh,
            SegmentedBody(-27, 27, 3, 14, POD_BOTTOM, POD_TOP),
            F.graphite,
            None,
            LOBE_SECTION,
        )
        for z in HATCHERY_RIBS:
            arch = curve([-13, 1, z], [13, 1, z], [0, 9, 0], 4)
            tendril(flesh, arch, [0.9, 0.9], 3, F.bone)
        for plate in HATCHERY_PLATES:
            top = plate[1]
            hull.bevel_slab(
                plate_outline(plate),
                [top - 1.2, top - 0.4, top + 0.8],
                [0.3, 0.8],
                H.base,
                None,
                H.panel,
            )
            for s in SIDES:
                neon.box(
                    [0.6, 0.4, plate[3] * 1.4],
                    N.hatchery,
                    Placement([s * 2.5, top + 0.7, plate[0]]),
                )
        # The launch hatch under the belly: dark doors in a ring of charge light.
        hull.cylinder(6, 1.6, 8, H.dark, Placement([0, POD_BOTTOM - 0.2, hatch_z]), 5.2)
        charge.ring(6.4, 0.5, 8, WHITE, Placement([0, POD_BOTTOM - 0.5, hatch_z]))
        for s in SIDES:
            charge.lathe(LAMP, 4, WHITE, Placement([s * 11.5, 3.5, hatch_z]))
            reactor_sac(p, [s * 7, 0.5, -27.5], 2.2, N.hatchery, F.sinew, 4)

    return build_enemy_model("hatchery", scene, N.hatchery, draw)
