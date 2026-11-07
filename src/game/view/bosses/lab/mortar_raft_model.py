# Copyright (c) 2026 Renaud Guillon
"""MB-MORTAR-RAFT-01 to MB-MORTAR-RAFT-04: the Mortar Raft, the Lab's L-25 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A gigantic flying raft seen from above: an old
barge hull down its middle, two pontoons under a plank deck on its left, a pontoon under a little
deck on its right, a boxy forward hull section lashed on its right bow, a deckhouse aft, cargo
under nets, a shed, a dozen small ducted lift propellers round its edges. Its parts (the mortar
emplacement, the wheelhouse cabin, the mast and its sail) and armour (the stern outriggers, the
tarpaulins) are in `mortar_raft_parts`; the lashings that snap are its rig (`mortar_raft_rig`).
A machine, not a creature (user request, 2026-11-06).
"""

import math

from game.config.bosses.lab.mortar_raft import (
    BARGE,
    BARGE_TOP,
    DECK,
    DECKHOUSE_TOP,
    HULL,
    LEFT_PONTOONS,
    MORTAR_RAFT,
    PLANK_TOP,
    PLANKS,
    PONTOON_AXIS,
    PONTOON_R,
    RIGHT_PONTOON,
    SIDE_DECK,
    SIDE_TOP,
    WHEELHOUSE,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.mortar_raft_parts import (
    GLASS,
    ROPE,
    TIMBER,
    N,
    box_outline,
    flat,
    mast,
    mortar_emplacement,
    outrigger,
    pontoon,
    prop,
    pt,
    rope,
    tarp,
    tarp_frame,
    wheelhouse_cabin,
)
from game.view.bosses.lab.mortar_raft_rig import build_raft_rig, raft_triangles
from game.view.bosses.mini_boss_greebles import lamps, seam, vent
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The small lift propellers round its edges (MB-MORTAR-RAFT-02): `[x, y, root x, root y]`, the arm
# from the root (on the hull or a deck) out to the duct.
PROPS = [
    [-45, -26, -37, -24],
    [-46, 6, -37, 4],
    [-30, -45, -26, -36],
    [6, -57, 4, -47],
    [46, -50, 39, -46],
    [47, -26, 39, -26],
    [38, 8, 30, 6],
    [-7, 53, -6, 43],
    [8, 52, 6, 43],
]  # type: list[list[float]]
# Cargo on the plank deck and the barge's deck, `[x, y, width, depth, height]`, under nets.
CARGO = [[-30, 10, 9, 7, 4], [-31, 0, 7, 6, 3], [6, -24, 6, 8, 3.4]]  # type: list[list[float]]


def _barge(p: Any) -> None:
    """Draw the old barge hull down its middle: its deck plates, hatches, bollards, lit gunwales."""
    p.hull.bevel_slab([flat(q[0], q[1]) for q in HULL], [0.6, DECK - 1.4, DECK], [2, 0.7], M.base)
    for y in [-30, -16, 2, 14]:
        seam(p.hull, flat(-15.5, y), flat(13.5, y), [DECK, 0.4, 0.3])
    seam(p.hull, flat(-1, -44), flat(-1, 40), [DECK, 0.5, 0.3])
    for hatch in [[-12, -6, -28, -18], [8, 12, -10, 0], [-14, -8, 2, 12]]:
        p.hull.slab(box_outline(hatch), [DECK, DECK + 0.9], M.panel)
    for y in [-40, -6, 24]:
        for x in [-15, 13]:
            p.hull.cylinder(0.9, 1.6, 6, M.dark, Placement(pt(x, y, DECK)))
    for s in [-1, 1]:
        gx = -16.4 if s < 0 else 14.2
        p.neon.box([0.4, 0.35, 56], N, Placement(pt(gx, -6, DECK - 0.2)))
    lamps(p.neon, [pt(-12, -45, DECK), pt(4, -47, DECK), pt(-11, 43, DECK), pt(9, 43, DECK)], 1, N)
    # Its deckhouse, aft (the wheelhouse cabin, its part, stands on it).
    p.hull.bevel_slab(
        box_outline(WHEELHOUSE), [DECK - 0.5, DECKHOUSE_TOP - 0.6, DECKHOUSE_TOP], [0, 0.6], M.panel
    )
    p.neon.box([0.4, 0.35, 14], N, Placement(pt(WHEELHOUSE[1] + 0.2, 26, DECKHOUSE_TOP - 0.4)))
    # A small shed forward left, its door lit.
    shed = [-15, -7, -36, -30]
    p.hull.bevel_slab(box_outline(shed), [DECK, DECK + 4.6, DECK + 5.4], [0, 0.9], M.panel)
    p.neon.box([2.4, 2.6, 0.3], N, Placement(pt(-11, -36.2, DECK + 0.4)))
    # The outriggers' hinge posts on its stern quarters (MB-MORTAR-RAFT-05).
    for s in [-1, 1]:
        hinge = pt(s * 16.5, 25, 2)
        p.hull.box([6, DECK - 1, 3.4], M.panel, Placement(hinge), M.base)
        p.hull.cylinder(1.4, DECK + 1, 6, M.dark, Placement(pt(s * 19, 25, 1)))


def _forward_hull(p: Any) -> None:
    """Draw the boxy forward hull section lashed on its right bow (its emplacement is a part)."""
    outline = [
        flat(BARGE[0], BARGE[2] + 4),
        flat(BARGE[0] + 4, BARGE[2]),
        flat(BARGE[1] - 3, BARGE[2] + 1),
        flat(BARGE[1], BARGE[2] + 5),
        flat(BARGE[1], BARGE[3]),
        flat(BARGE[0], BARGE[3]),
    ]
    p.hull.bevel_slab(outline, [1, BARGE_TOP - 1.2, BARGE_TOP], [1.6, 0.6], M.panel, None, M.base)
    for x in [22.5, 28.5, 34.5]:
        seam(p.hull, flat(x, BARGE[2] + 2), flat(x, BARGE[3] - 1), [BARGE_TOP, 0.4, 0.3])
    p.neon.box([0.4, 0.35, 26], N, Placement(pt(BARGE[1] - 0.2, -36, BARGE_TOP - 0.3)))
    # Its lashings to the barge: ropes over the gap, timber fenders.
    for y in [-44, -36, -26]:
        rope(p.bare, pt(12.5, y, DECK - 0.2), pt(BARGE[0] + 1.5, y + 1, BARGE_TOP - 0.2), 0.6, ROPE)
        p.flesh.box([3, 2, 2.4], TIMBER, Placement(pt(15.6, y, DECK - 3)))


def _left_raft(p: Any) -> None:
    """Draw the two pontoons under the plank deck on its left, and the cargo under nets on it."""
    for q in LEFT_PONTOONS:
        pontoon(p, q[0], [q[1], q[2]], PONTOON_R, PONTOON_AXIS)
    planks = [PLANKS[0], PLANKS[1] + 1.5, PLANKS[2], PLANKS[3]]
    p.flesh.slab(box_outline(planks), [PLANK_TOP - 1, PLANK_TOP], TIMBER)
    for k in range(9):
        y = PLANKS[2] + 2.5 + k * 5.6
        p.bare.box([planks[1] - planks[0], 0.15, 0.3], M.dark, Placement(pt(-27, y, PLANK_TOP)))
    for x in [PLANKS[0] + 1.5, -19.5]:
        p.flesh.box([1.6, 1.4, 50], TIMBER, Placement(pt(x, -5, PLANK_TOP - 0.4)))
    p.neon.box([0.4, 0.35, 44], N, Placement(pt(PLANKS[0] + 0.3, -5, PLANK_TOP)))
    for c in CARGO:
        base = PLANK_TOP if c[0] < -17 else DECK
        p.flesh.box([c[2], c[4], c[3]], TIMBER, Placement(pt(c[0], c[1], base)), M.panel)
        for k in [-1, 0, 1]:
            a = pt(c[0] - c[2] * 0.55, c[1] + k * c[3] * 0.3, base + 0.2)
            b = pt(c[0] + c[2] * 0.55, c[1] + k * c[3] * 0.3, base + 0.2)
            top_a = [a[0] - math.copysign(c[2] * 0.08, a[0] - b[0]), base + c[4] + 0.1, a[2]]
            top_b = [b[0] + math.copysign(c[2] * 0.08, a[0] - b[0]), base + c[4] + 0.1, b[2]]
            rope(p.bare, a, top_a, 0.3, ROPE)
            rope(p.bare, top_a, top_b, 0.3, ROPE)
            rope(p.bare, top_b, b, 0.3, ROPE)
        rope(
            p.bare,
            pt(c[0], c[1] - c[3] * 0.5, base + c[4] + 0.1),
            pt(c[0], c[1] + c[3] * 0.5, base + c[4] + 0.1),
            0.3,
            ROPE,
        )


def _right_raft(p: Any) -> None:
    """Draw the pontoon on its right and the little deck over it (the flak rotor's)."""
    pontoon(p, RIGHT_PONTOON[0], [RIGHT_PONTOON[1], RIGHT_PONTOON[2]], 5, 5)
    p.flesh.bevel_slab(
        box_outline(SIDE_DECK), [SIDE_TOP - 1.4, SIDE_TOP - 0.3, SIDE_TOP], [0, 0.4], TIMBER
    )
    for y in [-7, 6]:
        beam = [10, SIDE_DECK[0] + 3, y - 1, y + 1]
        p.flesh.slab(box_outline(beam), [DECK - 0.6, SIDE_TOP - 0.6], TIMBER)
        rope(p.bare, pt(12, y - 1.2, DECK + 0.2), pt(18, y - 1.2, SIDE_TOP - 0.2), 0.5, ROPE)
    p.neon.box([0.4, 0.35, 22], N, Placement(pt(SIDE_DECK[1] - 0.2, 3, SIDE_TOP)))
    vent(p.hull, pt(22, -7.5, SIDE_TOP), [4, 3], 3)
    p.bare.box([3, 0.3, 2], GLASS, Placement(pt(28, -7.5, SIDE_TOP)))


def _props(p: Any) -> None:
    """Draw the small ducted lift propellers round its edges (MB-MORTAR-RAFT-02)."""
    for q in PROPS:
        prop(p, [q[0], q[1]], [q[2], q[3]], 8, 4.2)


def build_mortar_raft(scene: Any) -> Any:
    """MB-MORTAR-RAFT-01, MB-MORTAR-RAFT-04: the Mortar Raft.

    A lopsided flying raft about 3.6 L across, pale green lights: its mortars, its wheelhouse
    turret and the core guns under its tarpaulins (their mounts, drawn by `build_boss_model`,
    BOSS-58). Its stern outriggers swing out as it transforms (MB-MORTAR-RAFT-05).
    """

    def core(p: Any) -> None:
        _left_raft(p)
        _right_raft(p)
        _barge(p)
        _forward_hull(p)
        _props(p)

    return build_boss_model(
        MORTAR_RAFT,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "mortar-barge": mortar_emplacement,
                "wheelhouse": wheelhouse_cabin,
                "mast": mast,
            },
            "rig": {"build": build_raft_rig, "triangles": raft_triangles},
            "armour": {
                "outrigger-right": {"whole": outrigger(1)},
                "outrigger-left": {"whole": outrigger(-1)},
                "bow-guns-tarp": {
                    "whole": tarp("bow-guns", DECK),
                    "frame": tarp_frame("bow-guns", DECK),
                },
                "deck-gun-tarp": {
                    "whole": tarp("deck-gun", PLANK_TOP),
                    "frame": tarp_frame("deck-gun", PLANK_TOP),
                },
                "stern-mortar-tarp": {
                    "whole": tarp("stern-mortar", DECK),
                    "frame": tarp_frame("stern-mortar", DECK),
                },
                "flak-rotor-tarp": {
                    "whole": tarp("flak-rotor", SIDE_TOP),
                    "frame": tarp_frame("flak-rotor", SIDE_TOP),
                },
            },
        },
    )
