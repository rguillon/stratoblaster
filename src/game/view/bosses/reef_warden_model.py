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
    turret,
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


def _draw_body(p: Any) -> None:
    """Draw the reef creature's body (MB-REEF-WARDEN-02).

    A teal ray-like mantle lined with a cyan vein, a dark shelled back along its spine, bone ribs
    and coral barbs, gill glands either side.
    """
    mantle(p, MANTLE, SKIRT, F.teal, CYAN)
    neon_band(p.neon, MANTLE, [-3.4, -1.1], [0.97, 1], CYAN)
    mantle(p, scale_outline(MANTLE, 0.7, 0, -3), [SKIRT[1] - 1, SKIRT[1] + 1.5], F.graphite)
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
        for z in [-8, 0, 8]:
            vein_line(p, [s * 13, 4.5, z], [s * 28, 3.4, z - 6], [0, 1, 0], 0.9, CYAN)
        gland(p, [s * 20, 3.5, 14], 2, CYAN)
        tentacle(p, [s * 8, 2, -28], [s * 14, 1, -36], [s * 3, 0, 0], [2, 0.3], F.teal)
    barbs(p, [0, 13, -16], {"count": 3, "spacing": 0.1, "size": 3, "dir": [0, 1, -0.3]})
    eyes(p, [0, 9.5, 23], {"count": 2, "size": 1.3, "spacing": 6}, CYAN)


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


def _prow_turret(p: Any, at: Vec3) -> None:
    """Add the prow cannon (the core's gun), grafted on the snout, turning around its pivot `at`."""
    turret(
        p,
        offset(at, 0, SKIRT[1], 0),
        {
            "radius": 7,
            "barrels": 1,
            "gap": 0,
            "bore": 1.5,
            "length": 7,
            "neon": CYAN,
        },
    )


def _cannon(p: Any, at: Vec3) -> None:
    """Add a side cannon (MB-REEF-WARDEN-03).

    An armoured coral growth on the flank under its twin-barrelled turret, a feeding sac behind it,
    barbs before it.
    """
    r = radius_of(REEF_WARDEN.stats.parts, 0, 14)
    growth(p, offset(at, 0, -1, 0), r * 0.95, CYAN, {"flesh": F.graphite, "height": 0.32})
    sac(p, offset(at, sign_of(at[0]) * 5, 1, -9), 4, F.slate, {"stretch": 0.5})
    barbs(p, offset(at, 0, 2, 9), {"count": 3, "spacing": 4, "size": 3, "dir": [0, 0.3, 1]})


def _cannon_turret(p: Any, at: Vec3) -> None:
    """Add a side cannon's twin-barrelled turret."""
    turret(
        p,
        offset(at, 0, 4, 0),
        {
            "radius": radius_of(REEF_WARDEN.stats.parts, 0, 14),
            "barrels": 2,
            "gap": 5,
            "bore": 1.6,
            "length": 9,
            "neon": CYAN,
            "hatch": -sign_of(at[0]),
        },
    )


def build_reef_warden(scene: Any) -> Any:
    """MB-REEF-WARDEN-01, MB-REEF-WARDEN-04: the Reef Warden, a wide ray-like reef creature.

    A cyan vein ring round its mantle and a prow cannon grafted on its snout; its two side cannons
    grow from its flanks.
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
            "turrets": {
                "core": _prow_turret,
                "cannon-left": _cannon_turret,
                "cannon-right": _cannon_turret,
            },
        },
    )
