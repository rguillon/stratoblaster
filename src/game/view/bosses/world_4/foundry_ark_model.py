# Copyright (c) 2026 Renaud Guillon
"""FB-FOUNDRY-ARK-01 to FB-FOUNDRY-ARK-07, 4-4: the Foundry Ark.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera; +X is the screen's
left. A huge flying foundry: an iron deck carrying a blast furnace at its heart, slag channels
glowing from it to the crucibles aft, a chimney row on the foredeck, a missile battery on the bow
and outriggers out to the rail cannons.

FB-FOUNDRY-ARK-02: a living colossus, its broad back scorched flesh ribbed in bone, its furnace a
swollen heart, slag running in its veins, its stacks, engines, rails and guns metal grafts.
"""

import math

from game.config.bosses.world_4.foundry_ark import (
    ARK_PARTS,
    ARK_TAPS,
    ARK_THROAT,
    FOUNDRY_ARK,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import grille
from game.view.bosses.mini_boss_greebles import seam, vent
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H
from game.view.bosses.overlord_city import box2d, edge_lights, symmetric
from game.view.bosses.world_4.foundry_ark_armour import FOUNDRY_ARK_ARMOUR
from game.view.bosses.world_4.foundry_ark_parts import (
    ARK_ORANGE,
    ARK_RED,
    DECK_TOP,
    MOLTEN,
    battery,
    chimney_row,
    crucible,
    rail_cannon,
    rail_mount,
)
from game.view.bosses.world_4.foundry_ark_yard import draw_yard
from game.view.bosses.world_4.living_forge import (
    SKIN,
    back_ribs,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import SIDES, flip_x
from render.geometry.organic import RibSpec
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The deck (right half, front to tail), closed across the bow.
DECK = symmetric(
    [
        [16, 98],
        [40, 86],
        [56, 60],
        [60, 20],
        [62, -40],
        [56, -76],
        [42, -94],
        [14, -98],
    ],
    100,
)
# The right outrigger (mirrored on the left), out to the rail cannon's turntable.
OUTRIGGER = [
    [56.0, 28.0],
    [80.0, 24.0],
    [86.0, 18.0],
    [86.0, 4.0],
    [80.0, -2.0],
    [56.0, -8.0],
]
# The engine block across the stern.
ENGINES = box2d(70, 12, [0, -94])
# The blast furnace's octagonal hearth (a lathe profile), its top flat under the crown plate the
# stack stands on (its spine armour, `foundry_ark_armour`).
HEARTH = [
    [25.0, 0.0],
    [25.0, 9.0],
    [22.0, 12.0],
    [21.0, 13.8],
]
HEARTH_FOOT = DECK_TOP - 1
# The slag channels from the furnace out to each crucible (the right one; mirrored).
CHANNEL = [
    [18.0, -14.0],
    [36.0, -28.0],
    [ARK_PARTS.crucible[0] - 8.0, -ARK_PARTS.crucible[1]],
]


def _flipped(outline: Any) -> Any:
    """`flipX` of an outline (enemy_shapes types its points as tuples)."""
    mirrored: Any = flip_x(outline)
    return mirrored


def _draw_hull(p: Any) -> None:
    """Draw the deck with its lit rim, the outriggers, the engine block, rust and soot.

    The fore flank and aft wing plates lying on the deck, with the dressing that stands on them,
    are its armour (`foundry_ark_armour`).
    """
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    flesh.bevel_slab(DECK, [-10, -3, DECK_TOP], [3, 3], SKIN.base, None, SKIN.dark)
    back_ribs(p, [-80, -66, 60, 72], RibSpec(46, 0, 5.5, 1.2))
    edge_lights(neon, DECK, [1, 2, 3, 4, 13, 14, 15, 16], [-3, -1.8], ARK_ORANGE)
    hull.bevel_slab(ENGINES, [-8, -1, 7], [1, 1.5], H.dark, None, H.panel)
    for s in SIDES:
        wing = OUTRIGGER if s > 0 else _flipped(OUTRIGGER)
        flesh.bevel_slab(wing, [-5, -1, DECK_TOP - 0.6], [1, 2], SKIN.panel, None, SKIN.dark)
        # The magma vein's stern run; its middle run is on the aft wing plate.
        magma_vein(p, [[s * 20, DECK_TOP + 0.3, -50], [s * 29, DECK_TOP + 0.3, -45]], 1.6, MOLTEN)
        glands(p, [[s * 18, DECK_TOP, 84]], 2.6, ARK_ORANGE)
        edge_lights(neon, wing, [0, 1, 2, 3, 4], [-2, -1], ARK_ORANGE)
        vent(hull, [s * 48, DECK_TOP, -60], [8, 10], 4)
        grille(hull, [s * 26, -72], [14, 10], [5, DECK_TOP + 0.05])
        seam(hull, [s * 8, 96], [s * 8, -90], [DECK_TOP, 1.4, 0.6], SHADE["edge"])


def _draw_furnace(p: Any) -> None:
    """Draw the blast furnace (the core): hearth, glowing slits, door and tap guns.

    Its stack on the crown plate is its spine armour; the throat's rings leave from its mouth.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    p.flesh.lathe(HEARTH, 8, SKIN.base, Placement([0, HEARTH_FOOT, 0], math.pi / 8))
    for k in range(8):
        a = (k * math.pi) / 4
        at = [math.sin(a) * 25.2, HEARTH_FOOT + 3, math.cos(a) * 25.2]
        if k != 0:
            neon.box([3, 4, 0.4], MOLTEN, Placement(at, a))
    throat = boss_point(ARK_THROAT[0], ARK_THROAT[1], ARK_THROAT[2])
    muzzle(throat, "ring")
    charge.box([9, 6, 0.6], WHITE, Placement([0, HEARTH_FOOT + 2, 25.2]))
    for m in ARK_TAPS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.box([4, 4, 5], H.dark, Placement([x, y - 2, z - 9]), SHADE["edge"])
        hull.cylinder(1.4, 7.6, 6, H.dark, Placement([x, y, z - 8.4], 0, QUARTER))
        charge.cylinder(1.45, 0.8, 6, WHITE, Placement([x, y, z - 0.8], 0, QUARTER))
        muzzle(tip)


def _draw_channels(p: Any) -> None:
    """Draw the slag channels glowing across the deck from the furnace to the crucibles."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    for s in SIDES:
        for i in range(1, len(CHANNEL)):
            a = CHANNEL[i - 1]
            b = CHANNEL[i]
            seam(flesh, [s * a[0], a[1]], [s * b[0], b[1]], [DECK_TOP, 5, 1], SKIN.panel)
            seam(neon, [s * a[0], a[1]], [s * b[0], b[1]], [DECK_TOP + 0.4, 2.6, 0.7], MOLTEN)
    # Rail lines down the deck for the ore wagons, between the furnace and the battery.
    for s in SIDES:
        seam(hull, [s * 3, 34], [s * 3, 70], [DECK_TOP, 0.8, 0.5], SHADE["edge"])


def _draw_stern(p: Any) -> None:
    """Draw the engines' nozzles at the stern, and red lamps on the deck's corners."""
    for s in SIDES:
        reactor_sacs(p, [[s * 12, 1, -100.2]], 5.5, MOLTEN)
        reactor_sacs(p, [[s * 28, 1, -100.2]], 4.2, MOLTEN)
        # On the deck's top face, inside its bevel (BOSS-52).
        p.neon.box([1.2, 0.8, 1.2], ARK_RED, Placement([s * 50, DECK_TOP + 0.2, -70]))
        p.neon.box([1.2, 0.8, 1.2], ARK_RED, Placement([s * 34, DECK_TOP + 0.2, 82]))


def build_foundry_ark(scene: Any) -> Any:
    """FB-FOUNDRY-ARK-01, FB-FOUNDRY-ARK-07: the Foundry Ark, a huge flying foundry (6 L).

    Sooty iron under orange neon: a blast furnace at its heart, slag channels glowing out to two
    crucibles hung in gantries aft, a chimney row on the foredeck, a missile battery on the bow and
    two rail cannons on outriggers.
    """

    def core(p: Any) -> None:
        _draw_hull(p)
        _draw_channels(p)
        draw_yard(p)
        _draw_furnace(p)
        _draw_stern(p)

    return build_boss_model(
        FOUNDRY_ARK,
        scene,
        ARK_ORANGE,
        {
            "core": core,
            "parts": {
                "rail-left": rail_mount,
                "rail-right": rail_mount,
                "chimneys": chimney_row,
                "battery": battery,
                "crucible-left": crucible,
                "crucible-right": crucible,
            },
            "turrets": {"rail-left": rail_cannon, "rail-right": rail_cannon},
            "armour": FOUNDRY_ARK_ARMOUR,
        },
    )
