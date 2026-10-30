"""P10-R11, 4-4: the Foundry Ark. Model space:
logical pixels, nose +Z (down the screen), Y up towards the camera; +X is the screen's left. A huge
flying foundry: an iron deck carrying a blast furnace at its heart, slag channels glowing from it to
the crucibles aft, a chimney row on the foredeck, a missile battery on the bow and outriggers out to
the rail cannons. P16-R06: a living colossus, its broad back scorched flesh ribbed in bone, its
furnace a swollen heart, slag running in its veins, its stacks, engines, rails and guns metal
grafts.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.foundry_ark import (  # noqa: E402
    ARK_PARTS,
    ARK_TAPS,
    ARK_THROAT,
    FOUNDRY_ARK,
)
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_greebles import grille, hazard  # noqa: E402
from game.view.bosses.mini_boss_greebles import seam, vent  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H  # noqa: E402
from game.view.bosses.overlord_city import box2d, edge_lights, symmetric  # noqa: E402
from game.view.bosses.world_4.foundry_ark_parts import (  # noqa: E402
    ARK_ORANGE,
    ARK_RED,
    DECK_TOP,
    MOLTEN,
    SOOT,
    battery,
    chimney_row,
    crucible,
    rail_cannon,
    rail_mount,
)
from game.view.bosses.world_4.foundry_ark_yard import draw_yard  # noqa: E402
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    SKIN,
    back_ribs,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import SIDES, decal, flip_x  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type OutlinePoint = list[float]
type Vec3 = list[float]
__pragma__("noskip")

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
# The blast furnace: its octagonal hearth, then its tapering stack (lathe profiles).
HEARTH = [
    [25.0, 0.0],
    [25.0, 9.0],
    [21.0, 13.0],
    [15.0, 15.0],
]
STACK = [
    [13.0, 0.0],
    [11.5, 12.0],
    [9.5, 18.0],
    [11.0, 19.5],
]
HEARTH_FOOT = DECK_TOP - 1
STACK_FOOT = HEARTH_FOOT + 15
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
    """The deck with its lit rim, the outriggers, the engine block, rust and soot."""
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
        magma_vein(
            p,
            [
                [s * 20, DECK_TOP + 0.3, -50],
                [s * 44, DECK_TOP + 0.3, -36],
                [s * 56, DECK_TOP + 0.3, -10],
            ],
            1.6,
            MOLTEN,
        )
        glands(
            p,
            [
                [s * 50, DECK_TOP, 10],
                [s * 18, DECK_TOP, 84],
            ],
            2.6,
            ARK_ORANGE,
        )
        edge_lights(neon, wing, [0, 1, 2, 3, 4], [-2, -1], ARK_ORANGE)
        for z in [-60, -20, 40]:
            vent(hull, [s * 48, DECK_TOP, z], [8, 10], 4)
        hazard(hull, [s * 40, 76], [10, 6], 4, DECK_TOP + 0.05)
        grille(hull, [s * 26, -72], [14, 10], [5, DECK_TOP + 0.05])
        decal(hull, box2d(20, 14, [s * 30, 40]), DECK_TOP + 0.04, SOOT)
        seam(hull, [s * 8, 96], [s * 8, -90], [DECK_TOP, 1.4, 0.6], SHADE["edge"])


def _draw_furnace(p: Any) -> None:
    """The blast furnace (the core): hearth, stack, glowing slits, the furnace door and tap guns."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    p.flesh.lathe(HEARTH, 8, SKIN.base, Placement([0, HEARTH_FOOT, 0], math.pi / 8))
    hull.lathe(STACK, 8, H.panel, Placement([0, STACK_FOOT, 0], math.pi / 8))
    hull.ring(11.2, 2.6, 8, SOOT, Placement([0, STACK_FOOT + 17, 0], math.pi / 8))
    neon.ring(12.3, 0.8, 8, ARK_ORANGE, Placement([0, STACK_FOOT + 6, 0], math.pi / 8))
    for k in range(8):
        a = (k * math.pi) / 4
        at = [math.sin(a) * 25.2, HEARTH_FOOT + 3, math.cos(a) * 25.2]
        if k != 0:
            neon.box([3, 4, 0.4], MOLTEN, Placement(at, a))
    throat = boss_point(ARK_THROAT[0], ARK_THROAT[1], ARK_THROAT[2])
    charge.cylinder(9, 0.4, 8, WHITE, Placement([0, throat[1] - 0.6, throat[2]]))
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
    """The slag channels glowing across the deck from the furnace to the crucibles."""
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
    """The engines' nozzles at the stern, and red lamps on the deck's corners."""
    for s in SIDES:
        reactor_sacs(p, [[s * 12, 1, -100.2]], 5.5, MOLTEN)
        reactor_sacs(p, [[s * 28, 1, -100.2]], 4.2, MOLTEN)
        p.neon.box([1.2, 0.8, 1.2], ARK_RED, Placement([s * 56, DECK_TOP + 0.2, -74]))
        p.neon.box([1.2, 0.8, 1.2], ARK_RED, Placement([s * 40, DECK_TOP + 0.2, 86]))


def build_foundry_ark(scene: Any) -> Any:
    """P10-R11: the Foundry Ark, a huge flying foundry (6 L) of sooty iron under orange neon: a
    blast
    furnace at its heart, slag channels glowing out to two crucibles hung in gantries aft, a chimney
    row on the foredeck, a missile battery on the bow and two rail cannons on outriggers."""

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
        },
    )
