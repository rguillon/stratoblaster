# Copyright (c) 2026 Renaud Guillon
"""FB-TRI-WING-HYDRA-01 to FB-TRI-WING-HYDRA-05, Lab L-1: the Tri-Wing Hydra.

A three-headed hydra with lime veins: a plated body, three long swaying necks fanned out in front
of it, each ending in a turret head, two shoulder plates, two membrane wings at its flanks and a
finned tail (its third wing). Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.bosses.lab.tri_wing_hydra import (
    ARMOUR_TOP,
    BELLY_TOP,
    NECK_CENTRE,
    NECK_LEFT,
    TRI_WING_HYDRA,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.tri_wing_hydra_parts import (
    LIME,
    head_drawing,
    laser_shoulder,
    missile_shoulder,
    neck_limbs,
)
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    gland,
    graft,
    polygon,
    rib_cage,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import (
    MembraneWing,
    SegmentedBody,
    carapace,
    membrane_wing,
    segmented_body,
)

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The body along Z (model space): its tail end, the seam between its back plating and its
# breastplate (the two armour regions, FB-TRI-WING-HYDRA-05), its front at the necks' roots.
BODY_TAIL = -47
BODY_SEAM = -9
BODY_NOSE = 32
BODY_WIDTH = 27
# The belly, flattened under the armour, and the armour's lowest point over it.
BELLY_HIGH = BELLY_TOP + 0.9
ARMOUR_LOW = BELLY_TOP - 0.4
# A wing's membrane from its root on the flank out to its tips (model space, the left one: +X).
WING_ROOT = [21, -12]
WING_TIPS = [[30, -3], [52, -10], [66, -22], [60, -34], [44, -36], [28, -28]]
WING_Y = 4
# The tail from the body's end, and its fin (the third wing) round its tip.
TAIL_TIP = [0, 3, -74]
FLUKE = [[0, -66], [11, -74], [14, -84], [6, -80], [0, -86], [-6, -80], [-14, -84], [-11, -74]]


def _back_girth(t: float) -> float:
    """Return the back plating's girth: from its narrow tail end to full at the seam."""
    return 0.35 + 0.65 * math.sin(math.pi * t / 2)


def _breast_girth(t: float) -> float:
    """Return the breastplate's girth: full at the seam, narrowing to the necks' roots."""
    return 0.45 + 0.55 * math.cos(math.pi * t / 2)


def _draw_core(p: Any) -> None:
    """Draw the core (FB-TRI-WING-HYDRA-02): the hydra's body without its armour.

    A long belly flattened under its plating, its membrane wings at its flanks, its tail with its
    fin, the necks' collar at its front, reactor sacs at its tail's root and lime veins.
    """
    segmented_body(
        p.flesh,
        SegmentedBody(BODY_TAIL, BODY_NOSE, 3, BODY_WIDTH, -3, BELLY_HIGH, 0.12),
        F.graphite,
    )
    for s in SIDES:
        root: list[Any] = [s * WING_ROOT[0], WING_ROOT[1]]
        tips: list[Any] = [[s * q[0], q[1]] for q in WING_TIPS]
        membrane_wing(
            p.flesh, p.flesh, MembraneWing(root, tips, WING_Y, 1, 2.2), [F.membrane, F.bone]
        )
        for q in [WING_TIPS[1], WING_TIPS[3]]:
            vein_line(
                p,
                [s * 24, WING_Y + 0.6, -14],
                [s * q[0] * 0.92, WING_Y + 0.6, q[1] * 0.92],
                [0, 0.6, 0],
                0.6,
                LIME,
            )
        reactor_sac(p, [s * 9, 2, -45], 2.6, LIME)
        vein_line(p, [s * 25, 3, 20], [s * 25, 3, -30], [s * 2, 1, 0], 0.9, LIME)
    tentacle(p, [0, 3.5, -40], TAIL_TIP, [0, 2, 0], [7, 2.2], F.sinew, 6)
    p.flesh.bevel_slab(FLUKE, [2.2, 3, 3.8], [0.4, 0.6], F.membrane)
    vein_line(p, [0, 6.5, -44], [0, 4.5, -70], [0, 1.5, 0], 0.8, LIME)
    # The collar the three necks grow out of, at the body's front.
    for root in [NECK_LEFT, [-NECK_LEFT[0], NECK_LEFT[1]], NECK_CENTRE]:
        graft(p, polygon(6, 6.2), [3, 6.5], [-root[0], 0, -root[1]], {"color": M.base})


def _draw_back(p: Any) -> None:
    """Draw the back plating (FB-TRI-WING-HYDRA-05): the armour shed at its first transformation.

    A ridged carapace over the rear of the body, bone ribs clamped over it, a lime vein down its
    spine and glands on its flanks; the racks lie under it.
    """
    carapace(
        p.flesh,
        SegmentedBody(
            BODY_TAIL,
            BODY_SEAM,
            2,
            BODY_WIDTH * 0.92,
            ARMOUR_LOW,
            ARMOUR_TOP,
            None,
            _back_girth,
            [True, False],
        ),
        [F.slate, F.membrane],
    )
    rib_cage(p, [-36, -26, -16], {"halfWidth": 18, "y": BELLY_TOP + 3, "height": 7, "thickness": 1})
    spine(p, [0, ARMOUR_TOP - 0.2, -40], [0, ARMOUR_TOP + 0.4, -10], {"color": LIME, "bow": 1})
    for s in SIDES:
        gland(p, [s * 17, BELLY_TOP + 6, -22], 1.6, LIME)
    graft(p, polygon(5, 5, [1, 1.3]), [ARMOUR_TOP - 3.4, ARMOUR_TOP - 1.6], [-8, 0, -32])


def _draw_breast(p: Any) -> None:
    """Draw the breastplate (FB-TRI-WING-HYDRA-05): the armour shed at its second transformation.

    A ridged carapace from its middle to the necks' roots, a riveted keel plate down its middle,
    lime veins fanning out to the three necks; the batteries and the orb lie under it.
    """
    carapace(
        p.flesh,
        SegmentedBody(
            BODY_SEAM,
            BODY_NOSE,
            2,
            BODY_WIDTH * 0.92,
            ARMOUR_LOW,
            ARMOUR_TOP,
            None,
            _breast_girth,
            [False, True],
        ),
        [F.slate, F.membrane],
    )
    graft(p, polygon(6, 6, [0.8, 1.6]), [ARMOUR_TOP - 1.2, ARMOUR_TOP + 0.4], [0, 0, 2])
    for s in SIDES:
        vein_line(
            p, [s * 3, ARMOUR_TOP - 0.6, 10], [s * 13, ARMOUR_TOP - 5, 24], [0, 1, 0], 0.8, LIME
        )
        graft(
            p,
            polygon(4, 4, [1.4, 0.8]),
            [ARMOUR_TOP - 5.4, ARMOUR_TOP - 3.6],
            [s * 15, 0, -2],
            {"color": M.base},
        )
    vein_line(p, [0, ARMOUR_TOP + 0.2, 8], [0, ARMOUR_TOP - 3, 28], [0, 1, 0], 0.8, LIME)


def build_tri_wing_hydra(scene: Any) -> Any:
    """FB-TRI-WING-HYDRA-01, FB-TRI-WING-HYDRA-04: the Tri-Wing Hydra, with lime veins.

    A plated body with three swaying necks fanned out in front, turret heads at their ends, two
    shoulder plates, membrane wings and a finned tail.
    """
    right_root = [-NECK_LEFT[0], NECK_LEFT[1]]
    return build_boss_model(
        TRI_WING_HYDRA,
        scene,
        LIME,
        {
            "core": _draw_core,
            "parts": {
                "head-left": head_drawing(NECK_LEFT),
                "head-right": head_drawing(right_root),
                "head-centre": head_drawing(NECK_CENTRE),
                "shoulder-left": missile_shoulder,
                "shoulder-right": laser_shoulder,
            },
            "limbs": neck_limbs(),
            "armour": {"back": {"whole": _draw_back}, "breast": {"whole": _draw_breast}},
        },
    )
