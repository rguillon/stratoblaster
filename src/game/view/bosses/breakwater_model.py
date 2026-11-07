# Copyright (c) 2026 Renaud Guillon
"""MB-BREAKWATER-01 to MB-BREAKWATER-04, 1-2: the Breakwater Logical pixels, nose +Z.

Y up (towards the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.mini_bosses import BREAKWATER
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_greebles import lamps, mast
from game.view.bosses.mini_boss_shapes import (
    neon_band,
    offset,
    radius_of,
    sign_of,
    socket,
)
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    gland,
    graft,
    growth,
    hide,
    mantle,
    polygon,
    rib_cage,
    sac,
    scale_outline,
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


ORANGE = BOSS_LOOK.neon["breakwater"]

# The barge's hull seen from above: a long, square-cut hull, bulging where the mortars sit.
BARGE_HULL = [
    [-24, 27],
    [24, 27],
    [31, 20],
    [31, 6],
    [39, 0],
    [39, -24],
    [31, -30],
    [31, -34],
    [24, -40],
    [-24, -40],
    [-31, -34],
    [-31, -30],
    [-39, -24],
    [-39, 0],
    [-31, 6],
    [-31, 20],
]
# Heights of the shell's rim: its belly, its widest line, its top.
HULL_Y = [-5, -1, 4]
# The ram plate around its centre: a V of chamfered armour over the bow.
PLATE = [
    [0, 17],
    [20, 5],
    [21, -5],
    [15, -10],
    [-15, -10],
    [-21, -5],
    [-20, 5],
]
# The shell along Z: a forward shell (a hide from the waist `SHELL_SPLIT` to the nose) and, behind
# it, the back plating (the armour it sheds, MB-BREAKWATER-05): a carapace from `PLATING_BOTTOM` up
# to `SHELL_TOP` over the rear belly, flattened up to `REAR_BELLY_TOP` (just under the plating).
SHELL_TAIL = -41
SHELL_SPLIT = -14
SHELL_NOSE = 13
SHELL_WIDTH = 27
SHELL_TOP = 16
PLATING_BOTTOM = 7.7
REAR_BELLY_TOP = 8.9


def _draw_body(p: Any) -> None:
    """Draw the crab's body (MB-BREAKWATER-02): a wide mantle under a domed, plated shell.

    The forward shell with ribs over it and an orange vein along its spine, the rear belly flattened
    under its plating (the armour, `_draw_plating`), eyes on stalks at its front over its mouth
    (the bow turret).
    """
    deck = HULL_Y[2]
    mantle(p, BARGE_HULL, [HULL_Y[0], deck], F.sinew, ORANGE)
    neon_band(p.neon, BARGE_HULL, [-1.4, -0.4], [1.02, 1.02], ORANGE)
    hide(
        p,
        {
            "tail": SHELL_SPLIT,
            "nose": SHELL_NOSE,
            "width": SHELL_WIDTH,
            "bottom": deck - 1,
            "top": SHELL_TOP,
            "segments": 2,
            "shell": [F.slate, F.membrane],
            "belly": F.graphite,
        },
    )
    segmented_body(
        p.flesh,
        SegmentedBody(SHELL_TAIL, SHELL_SPLIT, 2, SHELL_WIDTH, deck - 1, REAR_BELLY_TOP, 0.15),
        F.graphite,
    )
    rib_cage(p, [-10, 0], {"halfWidth": 22, "y": deck, "height": 10, "thickness": 1.1})
    spine(p, [0, 14.2, -11], [0, 15.2, 8], {"color": ORANGE, "width": 1.4, "bow": 1.2})
    for s in SIDES:
        tentacle(p, [s * 4, deck + 3, 12], [s * 6, deck + 9, 19], [0, 1, 0], [0.9, 0.5], F.sinew, 3)
        eyes(p, [s * 6, deck + 9, 19], {"count": 1, "size": 1.3}, ORANGE)
        vein_line(p, [s * 10, 14, -10], [s * 26, deck + 1, -14], [s * 2, 3, 0], 1, ORANGE)


def _draw_plating(p: Any) -> None:
    """Draw the back plating (MB-BREAKWATER-05): the armour it sheds at its transformation.

    The rear shell, a carapace over the flattened rear belly from its middle to its tail: bone ribs
    clamped over it, an orange vein along its spine, glands on its flanks with veins running down
    them, and the grafts on it (the riveted back plate, the armour bands, the mast).
    """
    carapace(
        p.flesh,
        SegmentedBody(SHELL_TAIL, SHELL_SPLIT, 2, SHELL_WIDTH * 0.92, PLATING_BOTTOM, SHELL_TOP),
        [F.slate, F.membrane],
    )
    rib_cage(p, [-30, -20], {"halfWidth": 22, "y": 11.8, "height": 4.6, "thickness": 1.1})
    spine(p, [0, 14.6, -38], [0, 14.6, -17], {"color": ORANGE, "width": 1.4, "bow": 1.5})
    graft(p, polygon(6, 8, [1.2, 1]), [15, 16.6], [0, 0, -27])
    for s in SIDES:
        gland(p, [s * 16, 14, -28], 2, ORANGE)
        vein_line(p, [s * 8, 15.4, -24], [s * 20.5, 11, -27], [s * 2, 2, 0], 1, ORANGE)
        graft(p, polygon(5, 5, [0.8, 1.6]), [12.6, 14], [s * 19, 0, -24], {"color": M.base})
    mast(p, [11, 15, -22], 8, ORANGE)


def _draw_legs(p: Any) -> None:
    """Draw the crab's walking legs, three each side, folded under its rim (bone, jointed)."""
    for s in SIDES:
        for z in [-8, -20, -32]:
            knee = [s * 36, HULL_Y[2] + 4, z - 2]
            tentacle(p, [s * 24, HULL_Y[2], z], knee, [0, 2, 0], [2.4, 1.6], F.sinew, 4)
            tentacle(p, knee, [s * 40, HULL_Y[0], z - 6], [s, 0, 0], [1.6, 0.2], F.bone, 4)


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the shell rotor (BOSS-58): an armoured cap, a seam of light round it.

    It bursts off as the rotor comes into use.
    """
    graft(p, polygon(8, 6.8), [16.2, 18], [0, 0, 2], {"color": M.panel})
    graft(p, polygon(8, 4.6), [18, 19.6], [0, 0, 2], {"color": M.base})
    p.neon.ring(6.6, 0.25, 8, ORANGE, Placement([0, 17.6, 2], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    p.hull.ring(6.4, 0.9, 16, M.base, Placement([0, 16.4, 2]))
    p.neon.ring(6.4, 0.3, 16, ORANGE, Placement([0, 17.2, 2]))


def _draw_grafts(p: Any) -> None:
    """Grafts on the core: a plate on the forward shell (its rotor's seat, BOSS-58), lights.

    The riveted back plate, the armour bands and the mast are on its plating (`_draw_plating`).
    """
    graft(p, polygon(4, 6, [1.3, 0.7]), [15.2, 16.6], [0, 0, 2], {"color": M.base})
    for s in SIDES:
        lamps(
            p.neon,
            [[s * 27, HULL_Y[2] + 0.4, z] for z in [16, 2, -29]],
            1.2,
            ORANGE,
        )


def _ram_plate(p: Any, at: Vec3) -> None:
    """Add the ram plate (MB-BREAKWATER-03): no weapon, the crab's thick bony brow shield.

    A V of grafted armour on it, orange veins along its edge.
    """
    top = 9
    p.flesh.bevel_slab(PLATE, [-3, 1, top - 1.5], [1.5, 4], F.bone, Placement(at), F.sinew)
    neon_band(p.neon, PLATE, [0.6, 1.8], [1.02, 1.02], ORANGE, Placement(at))
    for side in SIDES:
        edge = offset(at, side * 16, top - 1.6, 3.5)
        vein_line(p, offset(at, side, top - 1.2, 12.5), edge, [0, 0.8, 0], 1, ORANGE)
    graft(p, scale_outline(PLATE, 0.55, 0, 2), [top - 1.6, top], at)
    barbs(p, offset(at, 0, 2, 15), {"count": 3, "spacing": 7, "size": 4, "dir": [0, 0.2, 1]})


def _mortar(p: Any, at: Vec3) -> None:
    """Add a mortar (MB-BREAKWATER-03): a swollen barnacle growth on the flank.

    Under its squat turret and its short, fat barrel (its mount, BOSS-58); a spawn sac beside it.
    """
    r = radius_of(BREAKWATER.stats.parts, 1, 13)
    growth(p, offset(at, 0, HULL_Y[2] - 2, 0), r, ORANGE, {"flesh": F.graphite, "height": 0.4})
    sac(p, offset(at, sign_of(at[0]) * 8, HULL_Y[2], 6), 3.5, F.slate, {"stretch": 0.7})


def build_breakwater(scene: Any) -> Any:
    """MB-BREAKWATER-01, MB-BREAKWATER-04: the Breakwater.

    A huge armoured shore crab with orange veins: a wide plated shell over jointed legs, a bony
    V-shaped ram plate over its snout, a turret in its mouth and a rotor on the plate grafted on its
    shell (its mounts, BOSS-58), and two barnacle mortars on its flanks.
    """

    def core(p: Any) -> None:
        _draw_body(p)
        _draw_legs(p)
        _draw_grafts(p)
        for s in SIDES:
            socket(p.hull, [s * 34, HULL_Y[2], -12], 8, 1)
            # The ram plate's grafted brackets on the snout.
            p.hull.box([4, 3, 8], M.dark, Placement([s * 13, HULL_Y[2] - 1, 24]))
            reactor_sac(p, [s * 16, -0.5, -40], 3.4, ORANGE)
        p.reactor([0, -0.5, -40], 3.8)

    return build_boss_model(
        BREAKWATER,
        scene,
        ORANGE,
        {
            "core": core,
            "parts": {"ram-plate": _ram_plate, "mortar-left": _mortar, "mortar-right": _mortar},
            "armour": {
                "back": {"whole": _draw_plating},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
