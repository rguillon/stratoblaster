# Copyright (c) 2026 Renaud Guillon
"""The Narwhal's armour (FB-NARWHAL-06, 2-1): the plating it sheds, drawn as pieces of its own.

Two regions (D-254), each a cap of the hull (`narwhal_hull.hull_cap`) with what stood on the back
there: the `back`, behind the hump, with its deck plates, gland, spines and blowhole; the `spine`,
the hump (the dorsal sail) and the forward deck with its frozen crust. Logical pixels, nose +Z, Y
up (towards the camera).
"""

from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.mini_boss_greebles import plate, rect
from game.view.bosses.world_2.floe_breaker_frost import FROST
from game.view.bosses.world_2.narwhal_details import back_dressing, hump_dressing
from game.view.bosses.world_2.narwhal_hull import (
    BACK_SPAN,
    CAP_BOTTOM,
    OVERLAP,
    SPINE_SPAN,
    N,
    hull_cap,
)
from game.view.bosses.world_2.narwhal_parts import SUB_SECTION
from game.view.bosses.world_2.w2_organic import (
    ICE_FLESH,
    crystals,
    gland,
    glow_vein,
    spine_row,
)
from game.view.enemies.enemy_shapes import SIDES, flip_x
from render.geometry.organic import RibSpec, ribs
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
# The flat back of `SUB_SECTION` (the hump is lofted with it).
BACK = 4
# The hump (the dorsal sail: loft stations, aft to front).
SAIL = [  # type: list[list[float]]
    [-8, 3, 15, 22],
    [-2, 5, 15, 27],
    [16, 5, 15, 27],
    [22, 3, 15, 23],
]
# The right sail plane (the screen's left: +X is the model's left side, mirrored for the other).
SAIL_PLANE = [  # type: list[list[float]]
    [4.5, 15],
    [14, 11],
    [14, 8],
    [4.5, 7],
]
# The emitter on the hump's top: a lathe profile (the core's spiral gun, its muzzle on the core).
EMITTER = [  # type: list[list[float]]
    [3, 0],
    [3.2, 1.2],
    [2, 2.6],
    [0, 3],
]
# The bone ribs round the body and the metal bands grafted round it: arches over the back from
# the cap's bottom (their ends just under it, where the armour's lowest point is).
RIB = RibSpec(15.5, CAP_BOTTOM + 0.6, 10.4, 0.8)
BAND = RibSpec(17.8, CAP_BOTTOM + 0.6, 17.2, 0.7)


def sail_paint(side: int, _band: int) -> Any:
    """Return the hump's flat top under its snow cap (FB-NARWHAL-05)."""
    if side == BACK:
        return ICE_FLESH.rime
    return None


def _band(p: EnemyParts, z: float) -> None:
    """Draw a metal band grafted round the body at `z`: an arch over the back."""
    ribs(p.hull, [z], BAND, H.panel)


def draw_hump(p: EnemyParts) -> None:
    """Draw the hump (FB-NARWHAL-02): the dorsal sail, its planes now fins, the emitter on top."""
    flesh = p.flesh
    neon = p.neon
    flesh.loft(SUB_SECTION, SAIL, ICE_FLESH.graphite, None, LoftOptions(False, sail_paint))
    edge_strips(
        neon,
        [
            [0, -7.6],
            [0, 21.6],
        ],
        0.8,
        [26.9, 27.5],
        N,
    )
    for s in SIDES:
        plane = SAIL_PLANE if s > 0 else flip_x(SAIL_PLANE)
        flesh.bevel_slab(
            plane, [21, 22, 23], [0.3, 0.6], ICE_FLESH.membrane, None, ICE_FLESH.graphite
        )
        crystals(flesh, [s * 12, 22, 9], 2.6, 2)
        # Feelers on the hump, of different heights.
        flesh.cylinder(0.8, 4 + s * 1.5, 4, ICE_FLESH.sinew, Placement([s * 2.2, 27, 2]), 0.2)
    p.hull.lathe(EMITTER, 8, H.dark, Placement([0, 27, 10]))
    neon.ring(3.3, 0.5, 8, N, Placement([0, 27.4, 10]))
    p.charge.cylinder(1.3, 1.6, 6, WHITE, Placement([0, 29.4, 10]), 0.4)


def back_armour(p: EnemyParts) -> None:
    """Draw the back's plating (FB-NARWHAL-06, region `back`): the cap behind the hump.

    The hull's upper half from `CAP_BOTTOM` up over `BACK_SPAN`, the bone ribs and a metal band
    round it, two deck plates, the gland, the rear spines of ice, crystals, lit veins down the
    flanks, the blowhole with its valve, a plate and a whip antenna. The lances lie folded under
    it.
    """
    hull_cap(p, BACK_SPAN[0] - OVERLAP, BACK_SPAN[1])
    ribs(p.flesh, [-36, -28], RIB, ICE_FLESH.bone)
    _band(p, -16)
    plate(p.hull, rect(5, 7), [17.6, 0.5], FROST.panel, Placement([0, 0, -18]))
    plate(p.hull, rect(4, 4), [15.6, 0.5], H.panel, Placement([0, 0, -38]))
    gland(p, [0, 17, -26], 1.6, N)
    spine_row(p.flesh, [0, 15.2, -37], [0, 15.9, -30], 2, 3.5)
    crystals(p.flesh, [6, 16.6, -32], 3.4)
    for s in SIDES:
        glow_vein(p, [s * 5, 16, -14], [s * 12.5, 8, -40], 1, N)
    back_dressing(p, N)


def spine_armour(p: EnemyParts) -> None:
    """Draw the spine's plating (FB-NARWHAL-06, region `spine`): the hump and the forward deck.

    The hull's upper half from `CAP_BOTTOM` up over `SPINE_SPAN`, the bone ribs and a metal band
    round it, the hump with its fins, feelers, emitter, antenna and lamps, crystals, lit veins down
    the flanks and the frozen crust on the forward deck. The racks lie folded under it.
    """
    hull_cap(p, SPINE_SPAN[0], SPINE_SPAN[1] + OVERLAP)
    ribs(p.flesh, [28, 36], RIB, ICE_FLESH.bone)
    _band(p, -4)
    draw_hump(p)
    crystals(p.flesh, [-7, 16.6, 24], 2.6)
    for s in SIDES:
        glow_vein(p, [s * 5, 17, 20], [s * 12, 10, 39], 1, N)
    hump_dressing(p, N)
