# Copyright (c) 2026 Renaud Guillon
"""MB-REEF-WARDEN-01 to MB-REEF-WARDEN-04, 1-1: the Reef Warden Logical pixels, nose +Z.

Y up (towards the camera).
"""

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.mini_bosses import REEF_WARDEN
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
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import eyes, reactor_sac

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


CYAN = BOSS_LOOK.neon["reef-warden"]
# Navigation lights: red to port (+X, the screen's left), green to starboard.
PORT_RED = [1, 0.1, 0.12]
STARBOARD_GREEN = [0.2, 1, 0.35]

# The mantle seen from above: a wide ray, pointed at the snout, the cannons on its flanks.
MANTLE = [
    [0, 38],
    [12, 34],
    [24, 23],
    [35, 11],
    [40, 1],
    [38, -10],
    [28, -22],
    [14, -30],
    [-14, -30],
    [-28, -22],
    [-38, -10],
    [-40, 1],
    [-35, 11],
    [-24, 23],
    [-12, 34],
]
# Heights of the mantle: its belly, its back.
SKIRT = [-5, 3]
# The darker fold on the mantle, behind the plating (the fold's outline is the mantle's at 0.7,
# drawn back 3 px, cut straight at z 2 where the plating starts).
REAR_FOLD = [
    [25.9, 2],
    [28, -2.3],
    [26.6, -10],
    [19.6, -18.4],
    [9.8, -24],
    [-9.8, -24],
    [-19.6, -18.4],
    [-26.6, -10],
    [-28, -2.3],
    [-25.9, 2],
]
# Its back plating (the armour it sheds, MB-REEF-WARDEN-05): a horseshoe round its shelled back,
# from just behind the snout to its middle, the gatlings under its arms. The same outline as the
# `back` region of its design (config coordinates are [x, -z]).
PLATING = [
    [21, 2],
    [23, 8],
    [22, 16],
    [17, 24],
    [9, 30],
    [0, 33],
    [-9, 30],
    [-17, 24],
    [-22, 16],
    [-23, 8],
    [-21, 2],
    [-15, 2],
    [-15, 10],
    [-11, 18],
    [-7, 24],
    [0, 27],
    [7, 24],
    [11, 18],
    [15, 10],
    [15, 2],
]
# The plating lies on the mantle's back, sunk 0.3 px into it, as thick as the fold.
PLATING_HEIGHTS = [SKIRT[1] - 0.3, SKIRT[1] + 1.5]


def _draw_body(p: Any) -> None:
    """Draw the reef creature's body (MB-REEF-WARDEN-02).

    A teal ray-like mantle lined with a cyan vein, a dark shelled back along its spine, bone ribs
    and coral barbs (the gill glands are on its plating, `_draw_plating`).
    """
    mantle(p, MANTLE, SKIRT, F.teal, CYAN)
    neon_band(p.neon, MANTLE, [-3.4, -1.1], [0.97, 1], CYAN)
    mantle(p, REAR_FOLD, [SKIRT[1] - 1, SKIRT[1] + 1.5], F.graphite)
    hide(
        p,
        {
            "tail": -31,
            "nose": 24,
            "width": 12,
            "bottom": 3,
            "top": 13,
            "segments": 5,
            "shell": [F.slate, F.membrane],
            "belly": F.sinew,
        },
    )
    rib_cage(p, [-20, -12, -4, 4], {"halfWidth": 14, "y": 4, "height": 7, "thickness": 0.9})
    spine(p, [0, 13, -26], [0, 13.5, 18], {"color": CYAN})
    for s in SIDES:
        for z in [-8, 0]:
            vein_line(p, [s * 13, 4.5, z], [s * 28, 3.4, z - 6], [0, 1, 0], 0.9, CYAN)
        tentacle(p, [s * 8, 2, -28], [s * 14, 1, -36], [s * 3, 0, 0], [2, 0.3], F.teal)
    barbs(p, [0, 13, -16], {"count": 3, "spacing": 0.1, "size": 3, "dir": [0, 1, -0.3]})
    eyes(p, [0, 9.5, 23], {"count": 2, "size": 1.3, "spacing": 6}, CYAN)


def _draw_plating(p: Any) -> None:
    """Draw the back plating (MB-REEF-WARDEN-05): the armour it sheds at its transformation.

    A dark fold of plating in a horseshoe round the shelled back, lying on the mantle from just
    behind the snout to the middle; a gill gland on each arm and a vein running out across each.
    """
    mantle(p, PLATING, PLATING_HEIGHTS, F.graphite)
    top = PLATING_HEIGHTS[1]
    for s in SIDES:
        gland(p, [s * 20, top + 0.5, 14], 1.7, CYAN)
        vein_line(p, [s * 16, top + 0.2, 10], [s * 21, top + 0.2, 4], [0, 0.6, 0], 0.9, CYAN)


def _draw_grafts(p: Any) -> None:
    """Grafts: a riveted nose plate, a back plate, flank plates, exhausts, navigation lights."""
    graft(p, polygon(5, 6, [1.2, 0.8]), [11, 12.3], [0, 0, 14])
    graft(p, polygon(4, 5, [1.4, 0.8]), [12.6, 13.6], [0, 0, -10], {"color": M.base})
    for s in SIDES:
        graft(
            p,
            polygon(6, 4, [1, 1.4]),
            [SKIRT[1], SKIRT[1] + 0.8],
            [s * 26, 0, -14],
            {"color": M.base},
        )
    lamps(p.neon, [[27, SKIRT[1], -19]], 1.6, PORT_RED)
    lamps(p.neon, [[-27, SKIRT[1], -19]], 1.6, STARBOARD_GREEN)
    mast(p, [-4, 13.5, -16], 7, CYAN)


def _cannon(p: Any, at: Vec3) -> None:
    """Add a side cannon (MB-REEF-WARDEN-03).

    An armoured coral growth on the flank under its twin-barrelled turret (its mount, BOSS-58), a
    feeding sac behind it, barbs before it.
    """
    r = radius_of(REEF_WARDEN.stats.parts, 0, 14)
    growth(p, offset(at, 0, -1, 0), r * 0.95, CYAN, {"flesh": F.graphite, "height": 0.32})
    sac(p, offset(at, sign_of(at[0]) * 5, 1, -9), 4, F.slate, {"stretch": 0.5})
    barbs(p, offset(at, 0, 2, 9), {"count": 3, "spacing": 4, "size": 3, "dir": [0, 0.3, 1]})


def build_reef_warden(scene: Any) -> Any:
    """MB-REEF-WARDEN-01, MB-REEF-WARDEN-04: the Reef Warden, a wide ray-like reef creature.

    A cyan vein ring round its mantle, a prow turret grafted on its snout and a rotor on its spine
    (its mounts, BOSS-58); its two side cannons grow from its flanks.
    """

    def core(p: Any) -> None:
        _draw_body(p)
        _draw_grafts(p)
        for s in SIDES:
            socket(p.hull, [s * 34, 3, 2], 8, 1.2)
            reactor_sac(p, [s * 13, 5, -31], 3.4, CYAN, F.teal)
        p.reactor([0, -1, -30], 3)

    return build_boss_model(
        REEF_WARDEN,
        scene,
        CYAN,
        {
            "core": core,
            "parts": {"cannon-left": _cannon, "cannon-right": _cannon},
            "armour": {"back": {"whole": _draw_plating}},
        },
    )
