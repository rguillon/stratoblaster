"""P10-R11, 4-5: the Caldera Throne's keep over its core: three armoured tiers lit crimson, molten
slits in their walls, battlements, and the throne tower crowned in gold whose crown fires the core's
rings; the smokestacks aft, glowing at their mouths; watchtowers and lamps. Ported from
`bosses/world-4/caldera-throne-keep.ts`. Model space: logical pixels, nose +Z (down the screen),
Y up towards the camera.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.caldera_throne import CALDERA_CROWN  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.final_boss_greebles import studs  # noqa: E402
from game.view.bosses.final_boss_mechanism import armour, conduit  # noqa: E402
from game.view.bosses.mini_boss_shapes import SHADE, WHITE, H  # noqa: E402
from game.view.bosses.overlord_city import edge_lights  # noqa: E402
from game.view.bosses.world_4.caldera_throne_parts import (  # noqa: E402
    CRIMSON,
    DECK_TOP,
    GOLD,
    HEAT,
)
from game.view.bosses.world_4.living_forge import SKIN  # noqa: E402
from game.view.enemies.enemy_shapes import SIDES, around  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type OutlinePoint = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# P16-R06: the keep's lowest tier is the flesh of its back swelling up, the upper ones armour
# grafted on; its stacks are flesh spiracles, its watchtowers bone horns.


def _octagon(radius: float, centre: OutlinePoint) -> list[OutlinePoint]:
    """An octagon of `radius` (to its corners) around `[x, z]`, its faces square to the axes."""
    x = centre[0]
    z = centre[1]
    out: list[OutlinePoint] = []
    for a in around(8):
        turn = a + math.pi / 8
        out.append([x + math.sin(turn) * radius, z + math.cos(turn) * radius])
    return out


# The keep's tiers: radius, base and top heights.
TIERS = [
    [38.0, DECK_TOP - 1.0, 18.0],
    [29.0, 18.0, 28.0],
    [20.0, 28.0, 36.0],
]
# The throne tower on top of the keep: where (model z), its radius and top.
TOWER_Z = boss_point(CALDERA_CROWN[0], CALDERA_CROWN[1], CALDERA_CROWN[2])[2]
TOWER_RADIUS = 8
TOWER_TOP = 43
# The crown's charge light (lathe profile), up to the ring emitter.
CROWN_LIGHT = [
    [3.0, 0.0],
    [2.4, 3.0],
    [0.0, CALDERA_CROWN[2] - TOWER_TOP],
]
# The smokestacks aft: where (model x, z), their radius and top.
STACKS = [
    [24.0, -74.0, 4.6, 27.0],
    [40.0, -82.0, 3.8, 23.0],
]
# The watchtowers flanking the prow: where (model x, z), their radius and top.
WATCHTOWER_X = 26
WATCHTOWER_Z = 76
WATCHTOWER_RADIUS = 5
WATCHTOWER_TOP = 22
# The gold lamps along the deck's flanks (right half, `[x, z]` from and to).
LAMP_ROWS = [
    [
        [50.0, 46.0],
        [60.0, 20.0],
    ],
    [
        [60.0, -36.0],
        [52.0, -66.0],
    ],
]


def _draw_tiers(p: Any) -> None:
    """The three tiers, their edges lit crimson, molten slits in the lowest, battlements on it."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    for i in range(len(TIERS)):
        tier = TIERS[i]
        radius = tier[0]
        y0 = tier[1]
        y1 = tier[2]
        outline = _octagon(radius, [0, 0])
        if i == 0:
            armour(flesh, outline, [y0, y1], SKIN.base, 1.6, SKIN.dark)
        else:
            armour(hull, outline, [y0, y1], H.base, 1.6, H.panel)
        every = [k for k in range(len(outline))]
        edge_lights(neon, outline, every, [y1 - 3.2, y1 - 2.2], GOLD if i == 1 else CRIMSON)
    r0 = TIERS[0][0]
    y1 = TIERS[0][2]
    face = r0 * math.cos(math.pi / 8)
    for a in around(8):
        s = math.sin(a)
        c = math.cos(a)
        neon.box(
            [2.2, 6, 0.4],
            HEAT["molten"],
            Placement([s * (face + 0.3), DECK_TOP + 1.5, c * (face + 0.3)], a),
        )
        for d in [-0.28, 0.28]:
            along = face * math.tan(math.pi / 8) * d * 2
            at = [s * (face - 1.6) + c * along, y1, c * (face - 1.6) - s * along]
            hull.box([3.6, 2.6, 2.2], H.dark, Placement(at, a), SHADE["edge"])
    neon.box(
        [10, 2.4, 0.5],
        GOLD,
        Placement([0, 22, TIERS[1][0] * math.cos(math.pi / 8) + 0.3]),
    )


def _draw_tower(p: Any) -> None:
    """The throne tower: an armoured drum, a gold crown of spikes, its charge light on top."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    z = TOWER_Z
    radius = TOWER_RADIUS
    top = TOWER_TOP
    base = TIERS[2][2]
    hull.cylinder(radius + 2, 2, 8, H.panel, Placement([0, base, z], math.pi / 8), radius + 1)
    hull.cylinder(radius, top - base, 8, H.base, Placement([0, base, z], math.pi / 8), radius - 1)
    neon.ring(radius - 0.2, 0.9, 8, CRIMSON, Placement([0, top - 4, z], math.pi / 8))
    for a in around(6):
        at = [math.sin(a) * (radius - 2.4), top, z + math.cos(a) * (radius - 2.4)]
        neon.lathe(
            [
                [1.3, 0],
                [0, 6],
            ],
            4,
            GOLD,
            Placement(at, a, 0.25),
        )
    hull.cylinder(radius - 1.5, 0.8, 8, H.dark, Placement([0, top, z]))
    charge.lathe(CROWN_LIGHT, 6, WHITE, Placement([0, top, z]))
    muzzle(boss_point(CALDERA_CROWN[0], CALDERA_CROWN[1], CALDERA_CROWN[2]), "ring")


def _draw_stacks(p: Any) -> None:
    """The smokestacks aft: soot-black, banded crimson, their mouths glowing with the furnaces."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    for s in SIDES:
        for stack in STACKS:
            x = stack[0]
            z = stack[1]
            radius = stack[2]
            top = stack[3]
            at = [s * x, DECK_TOP, z]
            flesh.cylinder(radius, top - DECK_TOP, 6, SKIN.panel, Placement(at), radius * 0.85)
            hull.ring(radius * 0.9, 2, 6, HEAT["soot"], Placement([s * x, top - 2, z]))
            neon.ring(radius * 0.95, 0.8, 6, CRIMSON, Placement([s * x, DECK_TOP + 6, z]))
            neon.cylinder(radius * 0.7, 0.4, 6, HEAT["molten"], Placement([s * x, top - 0.3, z]))
        conduit(flesh, [s * 18, DECK_TOP + 3, -36], [s * 24, DECK_TOP + 3, -68], [1.6, 3])


def _draw_watch(p: Any) -> None:
    """The watchtowers by the prow, gold beacons on their roofs, and the deck's rows of lamps."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    x = WATCHTOWER_X
    z = WATCHTOWER_Z
    radius = WATCHTOWER_RADIUS
    top = WATCHTOWER_TOP
    for s in SIDES:
        at: Vec3 = [s * x, DECK_TOP, z]
        flesh.cylinder(radius, top - DECK_TOP, 6, SKIN.bone, Placement(at), radius * 0.8)
        hull.cylinder(radius * 1.25, 2, 6, H.panel, Placement([s * x, top, z]), radius * 0.9)
        neon.ring(radius * 0.95, 0.7, 6, CRIMSON, Placement([s * x, top - 4, z]))
        neon.box([1.6, 1.6, 1.6], GOLD, Placement([s * x, top + 2.2, z]))
        for row in LAMP_ROWS:
            a = row[0]
            b = row[1]
            studs(
                neon,
                [
                    [s * a[0], a[1]],
                    [s * b[0], b[1]],
                ],
                [5, 1.6],
                DECK_TOP + 0.06,
                GOLD,
            )


def draw_keep(p: Any) -> None:
    """The keep over the core, its throne tower, the smokestacks and watchtowers (P10-R11)."""
    _draw_tiers(p)
    _draw_tower(p)
    _draw_stacks(p)
    _draw_watch(p)
