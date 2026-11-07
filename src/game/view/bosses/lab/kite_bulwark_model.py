# Copyright (c) 2026 Renaud Guillon
"""MB-KITE-BULWARK-01 to MB-KITE-BULWARK-05: the Kite Bulwark, the Lab's L-15 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A huge box-kite glider fortress seen from
above: a long armoured nacelle down its middle, its wings (`kite_bulwark_wings`, moving pieces of
their own) spread wide either side on their spars, a winch bay at its tail paying out two tow
cables that trail far behind it to their drogues. Its wings fold back about their trailing roots as
it transforms (MB-KITE-BULWARK-05).
"""

import math

from game.config.bosses.lab.kite_bulwark import (
    CHIN_AT,
    KITE_BULWARK,
    NACELLE_TOP,
    ROTOR_AT,
    WINCH_GUN_AT,
    WINCH_TOP,
    WING_PIVOT,
    WING_Y,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import SHADE, grille, rod
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.kite_bulwark_wings import FABRIC, FABRIC_SIDE, N, kite_wings, pt
from game.view.bosses.mini_boss_greebles import lamps, seam
from game.view.enemies.enemy_shapes import FIGHTER_SECTION
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The nacelle's loft stations along Z (model: nose +Z), `[z, half width, bottom, top]`.
NACELLE = [
    [-32, 4, 3, 8],
    [-25, 8, 1, 11.5],
    [-12, 10, 0, 13],
    [20, 10, 0, 13],
    [29, 7.5, 1, 11.5],
    [36, 4, 3.5, 8.5],
    [39.5, 0, 6, 6],
]
# The tow cables: where they leave the winch's spools and where their drogues trail (config).
# The tail box: its half width and the y of its two spars (config).
TAIL_BOX: list[Any] = [17, [41, 55]]
CABLES: list[Any] = [[[6.5, 32, 7], [16, 72, 3]], [[-6.5, 32, 7], [-11, 80, 2]]]
GLASS = [0.12, 0.16, 0.2]


def _draw_nacelle(p: Any) -> None:
    """Draw the nacelle (MB-KITE-BULWARK-02): a long armoured hull, its deck and its glazed nose.

    Plates down its deck, a light line along each shoulder, the chin turret's seat, the rotor's
    collar (its hatch is drawn apart), vents behind it.
    """
    p.hull.loft(FIGHTER_SECTION, NACELLE, SHADE["base"])
    deck = [[0, 26], [5.5, 22], [6, -12], [4, -22], [-4, -22], [-6, -12], [-5.5, 22]]
    p.hull.bevel_slab(
        deck,
        [NACELLE_TOP - 2.4, NACELLE_TOP - 0.6, NACELLE_TOP + 0.2],
        [0, 0.8],
        SHADE["panel"],
        None,
        SHADE["light"],
    )
    for s in [-1, 1]:
        edge_strips(p.neon, [[s * 7.4, 24], [s * 8.6, -10], [s * 7, -22]], 0.45, [9.6, 10.4], N)
        seam(p.hull, [s * 3, 14], [s * 3.4, -6], [NACELLE_TOP + 0.2, 0.4, 0.25])
    # Its glazed nose: a smoked canopy and the light over it.
    p.hull.box([5, 1.6, 7], GLASS, Placement([0, 8.6, 31]))
    p.neon.box([4, 0.3, 0.6], N, Placement([0, 10.1, 33.6]))
    # The chin turret's seat (its mount, BOSS-58).
    chin = pt(CHIN_AT[0], CHIN_AT[1], NACELLE_TOP - 0.6)
    p.hull.cylinder(5.2, 0.9, 8, SHADE["dark"], Placement(chin, math.pi / 8))
    # The collar the spine rotor rises out of.
    collar = pt(ROTOR_AT[0], ROTOR_AT[1], NACELLE_TOP)
    p.hull.ring(5.4, 1, 12, SHADE["dark"], Placement(collar))
    grille(p.hull, [0, -12], [7, 6], [4, NACELLE_TOP + 0.25])


def _draw_hinges(p: Any) -> None:
    """Draw the wings' sockets on the nacelle's flanks (MB-KITE-BULWARK-05).

    A spar box at each wing's leading root, and the hinge drum at each trailing root (the wing
    folds back about it), a lit pin through it.
    """
    for s in [-1, 1]:
        lead = pt(s * 8.5, -12, WING_Y[0] - 1.2)
        p.hull.box([7, 4.6, 5], SHADE["mid"], Placement(lead), SHADE["light"])
        hinge = pt(s * WING_PIVOT[0], WING_PIVOT[1], WING_Y[0] - 2)
        p.hull.cylinder(3.2, 7.2, 8, SHADE["mid"], Placement(hinge, math.pi / 8))
        p.hull.box([5, 4, 6], SHADE["base"], Placement(pt(s * 7, WING_PIVOT[1], WING_Y[0] - 1.6)))
        p.neon.cylinder(1, 0.4, 8, N, Placement([hinge[0], WING_Y[0] + 5.2, hinge[2]]))


def _draw_winch_bay(p: Any) -> None:
    """Draw the winch bay at its tail: the bed the winch stands on, the spools and the cables.

    The two tow cables run from their spools far back behind it to their drogues: small cones
    with a lit ring.
    """
    bed = [[-7, -24], [7, -24], [8.5, -36], [5, -40], [-5, -40], [-8.5, -36]]
    p.hull.bevel_slab(bed, [1, 3.4, 4.2], [0, 0.8], SHADE["mid"])
    # The pedestal under the flak mortar's deck.
    p.hull.box(
        [5, WINCH_TOP - 4.6, 5], SHADE["dark"], Placement(pt(WINCH_GUN_AT[0], WINCH_GUN_AT[1], 4))
    )
    for s in [-1, 1]:
        spool = pt(s * 9.5, 32, 7)
        p.hull.cylinder(
            3.4,
            4,
            8,
            SHADE["dark"],
            Placement([spool[0] - 2, 7, spool[2]], math.pi / 2, math.pi / 2),
        )
        p.neon.ring(3.5, 0.5, 8, N, Placement([spool[0], 7, spool[2]], math.pi / 2, math.pi / 2))
    for cable in CABLES:
        a = cable[0]
        b = cable[1]
        start = pt(a[0] * 1.45, a[1], a[2])
        end = pt(b[0], b[1], b[2])
        rod(p.hull, start, end, 0.3, SHADE["mid"])
        # The drogue: a cone opening backwards, a lit ring round its mouth.
        p.hull.cylinder(1, 5, 8, SHADE["panel"], Placement(end, 0, -math.pi / 2), 3)
        p.neon.ring(3, 0.5, 8, N, Placement([end[0], end[1], end[2] - 5], 0, math.pi / 2))


def _draw_tail_box(p: Any) -> None:
    """Draw the tail box (MB-KITE-BULWARK-02): the box kite's rear cell behind the winch bay.

    A keel boom from the bay back to it, two spars across, two panes of fabric either side of the
    keel, their tall sides standing along the spars, a light along its back.
    """
    keel = [pt(0, 36, 4.5), pt(0, 56, 7)]
    rod(p.hull, keel[0], keel[1], 1.4, SHADE["mid"])
    for y in TAIL_BOX[1]:
        rod(p.hull, pt(-TAIL_BOX[0], y, 7.4), pt(TAIL_BOX[0], y, 7.4), 1.1, SHADE["mid"])
    for s in [-1, 1]:
        x0 = s * 2
        x1 = s * (TAIL_BOX[0] - 1)
        y0 = TAIL_BOX[1][0] + 1.2
        y1 = TAIL_BOX[1][1] - 1.2
        pane = [[-x0, -y0], [-x1, -y0], [-x1, -y1], [-x0, -y1]]
        p.hull.slab(pane, [8.6, 9.3], FABRIC_SIDE, None, FABRIC)
        rod(p.hull, pt(x0, y0, 9.5), pt(x1, y1, 9.5), 0.22, SHADE["dark"])
        rod(p.hull, pt(x0, y1, 9.5), pt(x1, y0, 9.5), 0.22, SHADE["dark"])
        for y in TAIL_BOX[1]:
            a = pt(x0, y, 0)
            b = pt(x1, y, 0)
            edge_strips(p.hull, [[a[0], a[2]], [b[0], b[2]]], 0.7, [7.4, 13], FABRIC_SIDE)
        tip = pt(s * TAIL_BOX[0], TAIL_BOX[1][1], 8.4)
        p.neon.box([1.4, 0.8, 1.4], N, Placement(tip))
    back = [
        pt(-TAIL_BOX[0] + 1, TAIL_BOX[1][1] + 1.2, 0),
        pt(TAIL_BOX[0] - 1, TAIL_BOX[1][1] + 1.2, 0),
    ]
    edge_strips(p.neon, [[q[0], q[2]] for q in back], 0.5, [8.1, 8.7], N)


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the spine rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], NACELLE_TOP)
    p.hull.cylinder(6, 1.4, 8, SHADE["panel"], Placement(at, math.pi / 8), 5.2)
    p.hull.box([6.4, 0.5, 1.2], SHADE["dark"], Placement([at[0], NACELLE_TOP + 1.3, at[2]]))
    p.neon.ring(5.7, 0.25, 8, N, Placement([at[0], NACELLE_TOP + 1, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a lit collar round the opening the rotor rises from."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], NACELLE_TOP)
    p.neon.ring(5.5, 0.4, 12, N, Placement(at))


def _pod(p: Any, at: Vec3) -> None:
    """Add a wingtip gun pod (MB-KITE-BULWARK-03): an armoured drum over its cradle.

    Its turret stands on top (its mount, BOSS-58); a lit band round it and fins fore and aft.
    """
    top = 13
    p.hull.lathe(
        [[5.4, 6], [6.6, 8], [6.6, top - 1.4], [5.6, top], [0, top]],
        8,
        SHADE["panel"],
        Placement([at[0], 0, at[2]], math.pi / 8),
    )
    p.neon.ring(6.7, 0.6, 8, N, Placement([at[0], 9.6, at[2]], math.pi / 8))
    for k in [-1, 1]:
        p.hull.box([1.2, 4.6, 6], SHADE["light"], Placement([at[0], 7, at[2] + k * 7.5]))


def _winch(p: Any, at: Vec3) -> None:
    """Add the tail winch (MB-KITE-BULWARK-03): a cable drum across its bed, in a cradle.

    The flak mortar stands on the cradle's deck (its mount, BOSS-58).
    """
    drum = [at[0] + 6.5, 7, -WINCH_GUN_AT[1] + 5]
    p.hull.cylinder(4, 13, 10, FABRIC_SIDE, Placement(drum, -math.pi / 2, math.pi / 2))
    for k in range(5):
        x = at[0] + 5 - k * 2.5
        p.neon.ring(4.1, 0.35, 10, N, Placement([x, 7, drum[2]], math.pi / 2, math.pi / 2))
    deck = pt(WINCH_GUN_AT[0], WINCH_GUN_AT[1], WINCH_TOP - 1)
    p.hull.box([10, 1.2, 9], SHADE["panel"], Placement(deck), SHADE["light"])
    for s in [-1, 1]:
        p.hull.box([1.6, WINCH_TOP - 5, 13], SHADE["mid"], Placement([s * 7.4, 4, deck[2] + 2]))
    lamps(
        p.neon,
        [[4.2, WINCH_TOP + 0.2, deck[2] - 3.8], [-4.2, WINCH_TOP + 0.2, deck[2] - 3.8]],
        1,
        N,
    )


def build_kite_bulwark(scene: Any) -> Any:
    """MB-KITE-BULWARK-01, MB-KITE-BULWARK-04: the Kite Bulwark.

    A box-kite glider fortress 3.8 L across with lime lights: its wingtip pods' turrets, its winch's
    flak mortar, the chin turret and the spine rotor (their mounts, drawn by `build_boss_model`,
    BOSS-58). Its wings fold back at its transformation (MB-KITE-BULWARK-05).
    """

    def core(p: Any) -> None:
        _draw_nacelle(p)
        _draw_hinges(p)
        _draw_winch_bay(p)
        _draw_tail_box(p)

    armour = kite_wings()
    armour["rotor-hatch"] = {"whole": _draw_hatch, "frame": _draw_hatch_frame}
    return build_boss_model(
        KITE_BULWARK,
        scene,
        N,
        {
            "core": core,
            "parts": {"pod-left": _pod, "pod-right": _pod, "winch": _winch},
            "armour": armour,
        },
    )
