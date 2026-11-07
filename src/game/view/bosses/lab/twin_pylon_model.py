# Copyright (c) 2026 Renaud Guillon
"""FB-TWIN-PYLON-01 to FB-TWIN-PYLON-05, Lab L-7: the Twin Pylon.

Logical pixels, nose +Z, Y up (towards the camera). Two lattice transmission pylons standing side by
side on a long base platform, an energy conduit sagging between their heads, the core a finned
capacitor block in the middle under it. Its pylons, parts and armour are in `twin_pylon_parts`.
"""

import math

from game.config.bosses.lab.twin_pylon import (
    ANNEX,
    CAP_HALF,
    CAP_STEP,
    CAP_TOP,
    CAP_Y,
    DECK_HALF,
    DECK_TOP,
    FRONT_GUN_AT,
    PROW,
    PYLON_HEAD,
    PYLON_TOP,
    PYLON_X,
    SAG,
    TWIN_PYLON,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import SHADE, grille, hazard, plate, rect, rod
from game.view.bosses.final_boss_mechanism import armour
from game.view.bosses.final_boss_shapes import WHITE, edge_strips
from game.view.bosses.lab.twin_pylon_parts import (
    N,
    box_outline,
    coil_head,
    draw_pylon,
    insulator,
    model_outline,
    pt,
    pylon_armour,
    transformer,
)
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The upper block of the capacitor starts this far along (config Y); its fins' spacing.
CAP_UPPER = -9
FIN_STEP = 3


def _deck_outline() -> list[Any]:
    """Return the platform's outline (config): its long deck, its prow and its rear annex."""
    x = DECK_HALF[0]
    y = DECK_HALF[1]
    return [
        [-PROW[0] + 3, PROW[1]],
        [PROW[0] - 3, PROW[1]],
        [PROW[0], -y],
        [x - 6, -y],
        [x, -y + 6],
        [x, y - 6],
        [x - 6, y],
        [ANNEX[0], y],
        [ANNEX[0], ANNEX[1]],
        [-ANNEX[0], ANNEX[1]],
        [-ANNEX[0], y],
        [-x + 6, y],
        [-x, y - 6],
        [-x, -y + 6],
        [-x + 6, -y],
        [-PROW[0], -y],
    ]


def _draw_deck(p: Any) -> None:
    """Draw the platform (FB-TWIN-PYLON-01): its deck, plates, grilles, lit edges and reactors."""
    p.hull.bevel_slab(
        model_outline(_deck_outline()),
        [0, DECK_TOP - 1.2, DECK_TOP],
        [0, 1],
        SHADE["dark"],
        None,
        SHADE["base"],
    )
    x = DECK_HALF[0]
    y = DECK_HALF[1]
    for s in [-1, 1]:
        # Lit lines along the deck's long front and back edges.
        edge_strips(
            p.neon,
            [[-s * (PROW[0] + 2), y - 1], [-s * (x - 7), y - 1]],
            0.6,
            [DECK_TOP, DECK_TOP + 0.1],
            N,
        )
        edge_strips(
            p.neon,
            [[-s * (ANNEX[0] + 2), -y + 1], [-s * (x - 7), -y + 1]],
            0.6,
            [DECK_TOP, DECK_TOP + 0.1],
            N,
        )
        # Deck plates between the pylon and the capacitor, a grille and hazard stripes at the ends.
        plate(p.hull, rect([-s * 22, -9], [14, 12]), DECK_TOP, SHADE["panel"], 0.4)
        grille(p.hull, [-s * 54, 10], [8, 12], [4, DECK_TOP + 0.05])
        hazard(p.hull, [-s * 77, 0], [3, 20], 3, DECK_TOP + 0.05)
        # Reactors under its back edge.
        p.reactor(pt(s * 56, y + 0.5, 3.4), 3)
    p.reactor(pt(0, ANNEX[1] + 0.5, 3.4), 3.4)


def _draw_capacitor(p: Any) -> None:
    """Draw the capacitor (the core, FB-TWIN-PYLON-02): a finned block under the conduit.

    A stepped base, an upper block with cooling fins along its flanks and lit slits between them,
    charge bars along its top that brighten as it readies a volley, its turret's seat on the step.
    """
    armour(
        p.hull,
        model_outline(box_outline([-CAP_HALF, CAP_HALF], CAP_Y)),
        [DECK_TOP - 0.5, CAP_STEP],
        SHADE["base"],
        1.4,
        SHADE["mid"],
    )
    upper = box_outline([-CAP_HALF + 1, CAP_HALF - 1], [CAP_UPPER, CAP_Y[1] - 1])
    armour(
        p.hull, model_outline(upper), [CAP_STEP - 0.5, CAP_TOP], SHADE["panel"], 1.2, SHADE["base"]
    )
    for s in [-1, 1]:
        y = CAP_UPPER + 1.5
        while y < CAP_Y[1] - 1.5:
            p.hull.box(
                [2.4, CAP_TOP - CAP_STEP - 1.5, 0.8],
                SHADE["dark"],
                Placement(pt(s * (CAP_HALF + 0.4), y, CAP_STEP)),
            )
            p.neon.box(
                [0.4, CAP_TOP - CAP_STEP - 3, 1.2],
                N,
                Placement(pt(s * (CAP_HALF - 0.6), y + FIN_STEP / 2, CAP_STEP + 0.8)),
            )
            y += FIN_STEP
        p.charge.box([1.4, 0.5, 9], WHITE, Placement(pt(s * 8, -2.5, CAP_TOP - 0.1)))
    # The front turret's seat on the step, and the lit band round the step.
    seat = pt(FRONT_GUN_AT[0], FRONT_GUN_AT[1], CAP_STEP - 0.4)
    p.hull.cylinder(5.8, 0.8, 8, SHADE["dark"], Placement(seat, math.pi / 8))
    ring = [[-CAP_HALF - 0.1, CAP_Y[0] - 0.1], [CAP_HALF + 0.1, CAP_Y[0] - 0.1]]
    edge_strips(p.neon, model_outline(ring), 0.5, [CAP_STEP - 3, CAP_STEP - 2.4], N)


def _sag(x: float) -> float:
    """Return the conduit's height at config X `x`: a parabola from the pylons' heads to `SAG`."""
    x0 = PYLON_X - PYLON_HEAD
    k = x / x0
    return float(SAG + (PYLON_TOP - 0.8 - SAG) * k * k)


def _draw_conduit(p: Any) -> None:
    """Draw the energy conduit (FB-TWIN-PYLON-02) sagging between the pylons' heads.

    A glowing cable between two dark ones, clamps along it, two feeders down to the capacitor.
    """
    x0 = PYLON_X - PYLON_HEAD
    steps = 10
    for k in range(steps):
        xa = -x0 + 2 * x0 * k / steps
        xb = -x0 + 2 * x0 * (k + 1) / steps
        rod(p.neon, pt(xa, 0, _sag(xa)), pt(xb, 0, _sag(xb)), 0.8, N)
        for y in [-2.2, 2.2]:
            rod(p.hull, pt(xa, y, _sag(xa) + 0.3), pt(xb, y, _sag(xb) + 0.3), 0.55, SHADE["base"])
        if k > 0:
            p.hull.box([1.2, 1.4, 6], SHADE["mid"], Placement(pt(xa, 0, _sag(xa) - 0.6)))
    for s in [-1, 1]:
        x = s * 9
        rod(p.hull, pt(x, 2.2, _sag(x)), pt(s * 9, 12, CAP_TOP), 0.5, SHADE["base"])


def build_twin_pylon(scene: Any) -> Any:
    """FB-TWIN-PYLON-01, FB-TWIN-PYLON-04: the Twin Pylon, 5 L across with electric blue lights.

    Its insulator stacks' lasers, coil heads' turrets, transformer's rotor and the capacitor's arc
    laser, front turret and rotor (their mounts, drawn by `build_boss_model`, BOSS-58).
    """

    def core(p: Any) -> None:
        _draw_deck(p)
        _draw_capacitor(p)
        draw_pylon(p, -PYLON_X)
        draw_pylon(p, PYLON_X)
        _draw_conduit(p)

    return build_boss_model(
        TWIN_PYLON,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "insulator-left": insulator,
                "insulator-right": insulator,
                "coil-left": coil_head,
                "coil-right": coil_head,
                "transformer": transformer,
            },
            "armour": pylon_armour(),
        },
    )
