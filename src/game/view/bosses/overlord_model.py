"""P07-R05, P16-R06: the Overlord, World 1's last boss (1-5), ported from
`bosses/overlord-model.ts`.
Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A city-sized
organism: a vast mantle with a city of living towers grown on its back, a shelled spine down its
middle carrying the citadel (its brain), membrane wings out to the laser cannons.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.final_bosses import OVERLORD  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.overlord_city import (  # noqa: E402
    OVERLORD_DECK,
    OVERLORD_NEON,
    box2d,
    edge_lights,
    symmetric,
)
from game.view.bosses.overlord_parts import (  # noqa: E402
    WING_TOP,
    draw_battery,
    draw_generator,
    draw_laser,
)
from game.view.bosses.overlord_skyline import draw_skyline  # noqa: E402
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    graft,
    mantle,
    polygon,
    rib_cage,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES, decal, flip_x  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    SegmentedBody,
    segmented_body,
)
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
QUARTER = math.pi / 2
N = OVERLORD_NEON

# The deck (right half, front to tail), the boulevard on it, and the right wing.
DECK = symmetric(
    [
        [26, 60],
        [52, 42],
        [64, 18],
        [64, -30],
        [52, -50],
        [36, -60],
    ],
    64,
)
BOULEVARD = symmetric(
    [
        [14, 54],
        [18, 26],
        [26, -10],
        [26, -46],
        [16, -54],
    ],
    56,
)
WING = [
    [60, 24],
    [98, 10],
    [104, 2],
    [104, -14],
    [96, -20],
    [60, -34],
]
# The citadel over the core: a stepped octagonal tower (lathe profile, bottom to top).
CITADEL = [
    [24, 0],
    [23, 7],
    [18, 10],
    [17.5, 16],
    [12, 19],
    [11, 24],
    [0, 25],
]
# The weapon array on the citadel's front.
GUN_DECK = [
    [-12, 14],
    [12, 14],
    [10, 34],
    [-10, 34],
]
LENS = [
    [0, -1.5],
    [3.2, 0],
    [0, 2.5],
]


def _draw_hull(p: Any) -> None:
    """The body (P16-R06): a vast purple mantle with a neon rim, a shelled spine down its middle
    (the boulevard) carrying the citadel, ribs across it, veins out to its edges, membrane
    wings out to the laser cannons on bone struts, swim bladders across its tail."""
    top = OVERLORD_DECK["top"]
    boulevard = OVERLORD_DECK["boulevard"]
    mantle(p, DECK, [-8, top], F.purple)
    edges: list[int] = []
    for i in range(len(DECK)):
        edges.append(i)
    edge_lights(p.neon, DECK, edges, [-2.6, -1.4], N)
    mantle(p, BOULEVARD, [top - 1, boulevard], F.crimson, N)
    rib_cage(
        p,
        [-44, -20, 20, 44],
        {"halfWidth": 30, "y": top - 1, "height": 7, "thickness": 1.3},
    )
    segmented_body(p.flesh, SegmentedBody(-68, -50, 3, 36, -7, 6), F.sinew)
    for s in SIDES:
        wing = WING if s > 0 else flip_x(WING)  # type: ignore[arg-type]
        p.flesh.bevel_slab(wing, [-4, -1, WING_TOP], [1, 2], F.membrane, None, F.purple)
        edge_lights(p.neon, wing, [0, 1, 2], [-1.5, -0.5], N)
        tentacle(p, [s * 56, 1, 20], [s * 102, 2, 2], [0, 2, 0], [2.6, 0.8], F.bone, 4)
        tentacle(p, [s * 56, 1, -30], [s * 100, 2, -16], [0, 2, 0], [2.4, 0.8], F.bone, 4)
        for z in [-40, -6, 30]:
            vein_line(p, [s * 24, boulevard, z], [s * 60, top + 0.2, z + 6], [0, 2, 0], 1.3, N)
        graft(
            p,
            polygon(5, 6, [1.4, 1]),
            [top - 0.4, top + 0.8],
            [s * 30, 0, 44],
            {"color": M.base},
        )
    barbs(p, [0, top, 58], {"count": 5, "spacing": 8, "size": 4, "dir": [0, -0.2, 1]})


def _draw_citadel(p: Any) -> None:
    """The citadel over the core (P16-R06): a swollen, tiered brain-head ringed with neon, eyes on
    its front, a ring emitter on top, the grafted weapon array before it."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    top = OVERLORD_DECK["top"]
    # Turned an eighth of a turn, a flat of the octagon faces the front.
    p.flesh.lathe(CITADEL, 8, F.crimson, Placement([0, top, 0], math.pi / 8))
    eyes(p, [0, top + 17, 17], {"count": 3, "size": 1.3, "spacing": 4}, N)

    def lit(r: float, y: float, h: float) -> None:
        neon.ring(r, h, 8, N, Placement([0, top + y, 0], math.pi / 8))

    lit(18.1, 12, 1.2)
    lit(11.9, 21.5, 1)
    # The ring emitter on top of the citadel.
    charge.lathe(
        [
            [5, 0],
            [3.5, 1.8],
            [0, 2.6],
        ],
        8,
        WHITE,
        Placement([0, top + 25, 0]),
    )
    muzzle([0, top + 27.6, 0], "ring")
    deck = OVERLORD_DECK["boulevard"]
    hull.bevel_slab(GUN_DECK, [deck, deck, deck + 9], [0, 1.5], H.base, None, H.panel)
    decal(neon, box2d(14, 1.2, [0, 24]), deck + 9.05, N)
    # A laser lens between twin cannons, all charging before they fire.
    axis = deck + 4.5
    hull.cylinder(4.2, 3, 8, H.dark, Placement([0, axis, 31], 0, QUARTER))
    charge.lathe(LENS, 6, WHITE, Placement([0, axis, 35.5], 0, QUARTER))
    muzzle([0, axis, 38], "laser")
    for s in SIDES:
        hull.cylinder(1.6, 10, 6, H.dark, Placement([s * 7, axis + 1, 28], 0, QUARTER))
        charge.cylinder(2, 1.6, 6, WHITE, Placement([s * 7, axis + 1, 38], 0, QUARTER))
        muzzle([s * 7, axis + 1, 39.6], None)


def _draw_hatches(p: Any) -> None:
    """The missile hatches on the boulevard behind the citadel, lit as missiles load."""
    hull = p.hull
    charge = p.charge
    muzzle = p.muzzle
    y = OVERLORD_DECK["boulevard"]
    graft(p, box2d(22, 18, [0, -34]), [y - 0.6, y], [0, 0, 0], {"color": M.base})
    for x in [-6, 6]:
        for z in [-30, -38]:
            decal(hull, box2d(6.4, 5.4, [x, z]), y + 0.03, H.dark)
            decal(charge, box2d(4.6, 3.6, [x, z]), y + 0.06, WHITE)
            muzzle([x, y + 0.06, z], "missile")


def _draw_core(parts: Any) -> None:
    """The core: body, city, citadel and hatches, four reactors in sacs across the tail."""
    _draw_hull(parts)
    draw_skyline(parts)
    _draw_citadel(parts)
    _draw_hatches(parts)
    for s in SIDES:
        reactor_sac(parts, [s * 12, -1, -68], 5.5, N)
        reactor_sac(parts, [s * 28, -1, -68], 4.2, N)


def build_overlord(scene: Any) -> Any:
    """P07-R05, P16-R06: the Overlord, a city-sized organism (6 L) under purple neon: living towers
    lit with window glands grown out of its vast mantle, two wing laser cannons, two missile
    batteries at the back, two shield generators in front, and a citadel over the core carrying a
    laser, twin cannons, a ring emitter and missile hatches."""
    return build_boss_model(
        OVERLORD,
        scene,
        N,
        {
            "core": _draw_core,
            "parts": {
                "laser-left": draw_laser,
                "laser-right": draw_laser,
                "battery-left": draw_battery,
                "battery-right": draw_battery,
                "generator-left": draw_generator,
                "generator-right": draw_generator,
            },
        },
    )
