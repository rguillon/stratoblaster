# Copyright (c) 2026 Renaud Guillon
"""FB-SIEGE-CRAWLER-03, FB-SIEGE-CRAWLER-05: the Siege Crawler's parts and armour.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. Its parts are
armoured growths on its shell under their gun mounts (drawn by `build_boss_model`, BOSS-58): the
cannon's mantlet on its head shield, a mortar cradle on each flank, a missile sponson on each rear
flank. Its armour: the middle deck plates and the head shield's cheeks, and the hatches over the
core's two late guns.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.siege_crawler import CHEEK_PLATES, DECK_PLATES, FLAK_AT, ROTOR_AT
from game.view.bosses.mini_boss_greebles import rect, vent
from game.view.bosses.mini_boss_shapes import offset, sign_of
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    gland,
    graft,
    polygon,
    sac,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


RED = BOSS_LOOK.neon["siege-crawler"]
# Heights of its shell: the belly's top, the thorax's plates, the cheeks under their armour.
BELLY_TOP = 2
PLEURA_TOP = 5.4
CHEEK_TOP = 4
# The deck plates and the cheek armour: from their bottom to their top.
DECK_Y = [5.1, 7.4, 8.6]
CHEEK_Y = [3.8, 6.6, 8]


def model_outline(outline: list[Any], side: float) -> list[Any]:
    """Return a design outline (X right, Y up) in model space, on `side` (1: the screen's left)."""
    return [[side * q[0], -q[1]] for q in outline]


def draw_cannon(p: Any, at: Vec3) -> None:
    """Add the front cannon's mantlet (FB-SIEGE-CRAWLER-03): a heavy armoured ring.

    It stands on the head shield's ridge under its three-barrelled turret (its mount), a riveted
    collar and a flesh sac feeding it from behind.
    """
    ring = polygon(8, 12.5, [1, 0.85])
    p.hull.bevel_slab(ring, [5, 7.6, 9], [0.5, 1.6], M.panel, Placement(at), M.base)
    p.neon.ring(12.2, 0.45, 8, RED, Placement(offset(at, 0, 7.4, 0), math.pi / 8))
    for s in SIDES:
        p.hull.box([3, 2.2, 7], M.dark, Placement(offset(at, s * 11.5, 7.5, -1), s * 0.3), M.panel)
        graft(p, polygon(4, 2.4, [1, 1.6]), [8.6, 9.3], offset(at, s * 7, 0, -6), {"color": M.base})
    sac(p, offset(at, 0, 5, -11), 5, F.slate, {"stretch": 0.55})
    vein_line(p, offset(at, 0, 9.5, -14), offset(at, 0, 8.6, -8), [0, 1, 0], 0.9, RED)


def draw_mortar(p: Any, at: Vec3) -> None:
    """Add a mortar's cradle (FB-SIEGE-CRAWLER-03): a swollen, armoured growth on the flank.

    Its mortar's turntable sits on top (its mount); ammunition sacs bulge beside it.
    """
    s = sign_of(at[0])
    p.flesh.lathe(
        [[11, 0], [11.5, 2.5], [9.5, 5.5], [7, 7], [0, 7.2]],
        8,
        F.graphite,
        Placement(offset(at, 0, 0.2, 0), math.pi / 8),
    )
    p.vein.ring(10.6, 0.5, 8, RED, Placement(offset(at, 0, 4, 0), math.pi / 8))
    graft(p, polygon(8, 8.2), [6.4, 7.2], at, {"color": M.base})
    for k in range(3):
        a = s * (0.7 + k * 0.8)
        sac(p, offset(at, math.sin(a) * 11, 3, math.cos(a) * 11), 2.6, F.slate, {"stretch": 0.7})
    barbs(p, offset(at, 0, 5, 10), {"count": 3, "spacing": 4, "size": 2.5, "dir": [0, 0.4, 1]})


def draw_missiles(p: Any, at: Vec3) -> None:
    """Add a missile sponson (FB-SIEGE-CRAWLER-03): an armoured box on the rear flank.

    Its block of four ports stands on it (its mount); a feed sac and a cable run into the shell.
    """
    s = sign_of(at[0])
    box = [[-9, -8], [9, -8], [10, 6], [6, 10], [-6, 10], [-10, 6]]
    p.hull.bevel_slab(box, [0.5, 4, 5.2], [0, 1.2], M.panel, Placement(at), M.base)
    p.neon.ring(10.4, 0.35, 6, RED, Placement(offset(at, 0, 3.6, 1), math.pi / 6))
    for k in [-1, 1]:
        p.hull.box([1.2, 1, 14], M.dark, Placement(offset(at, k * 8.5, 5.2, 1)))
    sac(p, offset(at, -s * 9, 2, -4), 4, F.slate, {"stretch": 0.6})
    vein_line(p, offset(at, -s * 8, 5, -4), offset(at, -s * 16, 6, -6), [0, 1.5, 0], 0.8, RED)


def draw_deck(p: Any) -> None:
    """Draw the middle deck plates (FB-SIEGE-CRAWLER-05): the armour shed at transformation 1.

    Two thick riveted plates on the thorax's side lobes, either side of its ridge, a vent and a red
    seam on each; the lances lie folded under them.
    """
    for s in SIDES:
        outline = model_outline(DECK_PLATES, s)
        p.hull.bevel_slab(outline, DECK_Y, [0.4, 1.2], M.panel, None, M.base)
        vent(p.hull, [s * 17, DECK_Y[2], -6], [7, 5], 3)
        p.neon.box([0.6, 0.4, 24], RED, Placement([s * 23.4, DECK_Y[1], -13]))
        for z in [0, -24]:
            p.hull.box([12, 0.6, 1.2], M.dark, Placement([s * 17, DECK_Y[2], z]))


def draw_cheeks(p: Any) -> None:
    """Draw the head shield's cheeks (FB-SIEGE-CRAWLER-05): the armour shed at transformation 2.

    Wide plated wedges from the cannon's collar out to the genal corners, ridged, a red vein along
    each; the racks lie folded under them.
    """
    for s in SIDES:
        outline = model_outline(CHEEK_PLATES, s)
        p.hull.bevel_slab(outline, CHEEK_Y, [0.4, 1.6], M.panel, None, M.base)
        for z in [24, 32]:
            p.hull.box([22, 0.8, 1.6], M.dark, Placement([s * 38, CHEEK_Y[2] - 0.3, z], s * 0.12))
        vein_line(p, [s * 20, CHEEK_Y[2], 36], [s * 58, CHEEK_Y[2] - 0.6, 24], [0, 1, 2], 0.9, RED)
        gland(p, [s * 48, CHEEK_Y[2] - 0.4, 30], 1.6, RED)


def _hatch(p: Any, at: list[Any], r: float, y: float) -> None:
    """Draw a hatch over a core gun (BOSS-58): an armoured cap, a seam of light round it."""
    spot = [-at[0], 0, -at[1]]
    p.hull.cylinder(r, 1.6, 8, M.panel, Placement(offset(spot, 0, y, 0), math.pi / 8), r * 0.9)
    p.hull.cylinder(r * 0.65, 1, 8, M.base, Placement(offset(spot, 0, y + 1.6, 0), math.pi / 8))
    p.neon.ring(r * 0.95, 0.25, 8, RED, Placement(offset(spot, 0, y + 1.2, 0), math.pi / 8))


def _collar(p: Any, at: list[Any], r: float, y: float) -> None:
    """Draw what a hatch leaves (BOSS-44): a collar round the opening its gun rises out of."""
    spot = [-at[0], y, -at[1]]
    p.hull.ring(r * 0.92, 1, 16, M.base, Placement(spot))
    p.neon.ring(r * 0.92, 0.3, 16, RED, Placement(offset(spot, 0, 1, 0)))


# The heights the core's hatches lie at: the ridge's seat under the rotor, the tail shield's under
# the flak mortar.
ROTOR_SEAT = 9.2
FLAK_SEAT = 6.8


def crawler_armour() -> dict[str, Any]:
    """Return the drawings of its armour regions (`drawing.armour`, D-254)."""

    def rotor_hatch(p: Any) -> None:
        _hatch(p, ROTOR_AT, 6.5, ROTOR_SEAT)

    def rotor_collar(p: Any) -> None:
        _collar(p, ROTOR_AT, 6.5, ROTOR_SEAT)

    def flak_hatch(p: Any) -> None:
        _hatch(p, FLAK_AT, 7, FLAK_SEAT)

    def flak_collar(p: Any) -> None:
        _collar(p, FLAK_AT, 7, FLAK_SEAT)

    return {
        "deck": {"whole": draw_deck},
        "cheeks": {"whole": draw_cheeks},
        "rotor-hatch": {"whole": rotor_hatch, "frame": rotor_collar},
        "flak-hatch": {"whole": flak_hatch, "frame": flak_collar},
    }


def draw_legs(p: Any) -> None:
    """Draw the rows of legs along both flanks (FB-SIEGE-CRAWLER-02), like a tank's tracks.

    Under a long armoured fender each side, eight short jointed bone legs, each bent the same way,
    a red light on each knee.
    """
    fender = rect(11, 64)
    for s in SIDES:
        p.hull.bevel_slab(fender, [0, 3.6, 5], [0, 1], M.panel, Placement([s * 61, 0, 2]), M.base)
        for z in range(8):
            zz = -26 + z * 8
            knee = [s * 69, 3, zz + 1]
            tentacle(p, [s * 62, 1.5, zz], knee, [0, 1.5, 0], [1.9, 1.4], F.sinew, 4)
            tentacle(p, knee, [s * 72, -3, zz - 2.5], [s, 0, 0], [1.4, 0.3], F.bone, 4)
            p.hull.box([8, 0.6, 1.4], M.dark, Placement([s * 61, 5, zz + 4]))
        p.neon.box([0.7, 0.5, 60], RED, Placement([s * 66.6, 3.6, 2]))
