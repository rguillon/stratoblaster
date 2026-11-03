# Copyright (c) 2026 Renaud Guillon
"""MB-EMBER-HERALD-01 to MB-EMBER-HERALD-04, 4-5: the Ember Herald, the mini boss of the Caldera.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera; +X is the screen's
left. MB-EMBER-HERALD-02: a living fire-wasp, its long flesh body ribbed in bone, scorched membrane
wings veined molten, bone spines and a metal spire and halo grafted on. The tail half of its body is
under the back plating it sheds (MB-EMBER-HERALD-11, `ember_herald_armour`).
"""

import math

from game.config.bosses.world_4.ember_herald import (
    EMBER_CROWN,
    EMBER_GUNS,
    EMBER_HERALD,
    EMBER_LANCE,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H
from game.view.bosses.overlord_city import edge_lights, symmetric
from game.view.bosses.world_4.ember_herald_armour import draw_plating
from game.view.bosses.world_4.ember_herald_parts import (
    GOLD,
    HEAT,
    ember_lance,
    embers,
    spike,
)
from game.view.bosses.world_4.living_forge import (
    SKIN,
    back_ribs,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, SIDES, around, canopy_paint
from render.geometry.organic import RibSpec
from render.geometry.outline import hypot2
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type OutlinePoint = list[float]
type Vec3 = list[float]
# __pragma__ ("noskip")


# The fuselage (loft stations, tail to nose): a long, hard-edged body closing to a needle nose, its
# tail half flattened to a deck `DECK` high under its back plating (the dome it sheds,
# MB-EMBER-HERALD-11), rising to its full height again ahead of it.
DECK = 2.6
FUSELAGE = [
    [-54.0, 6.0, 0.0, DECK],
    [-40.0, 9.0, 0.0, DECK],
    [-14.0, 11.0, 0.0, DECK],
    [-8.0, 10.8, 0.0, DECK],
    [-5.0, 10.5, 0.0, 10.8],
    [14.0, 9.5, 0.0, 10.0],
    [36.0, 6.5, 0.5, 7.5],
    [50.0, 3.5, 1.5, 4.5],
    [60.0, 0.0, 2.6, 2.6],
]
# The fuselage's back (sides of its section), sooted behind the canopy.
BACK = [2, 3, 4, 5]
# The bands of the fuselage that are sooted: the deck under the plating, behind the canopy.
SOOT_BANDS = 4
# The bands of the fuselage the canopy is painted on.
CANOPY_BANDS = [5, 6]

# The spiky wings seen from above (right half, front to tail): a forward spike off the wing root, a
# long spike at the tip, a sawtooth trailing edge and a spike at the tail.
WING = symmetric([
    [6, 34],
    [14, 16],
    [28, 7],
    [50, 14],
    [38, -2],
    [57, -24],
    [45, -24],
    [36, -33],
    [30, -46],
    [20, -36],
    [8, -40],
])
# Heights of the wing: belly, edge, top.
WING_Y = [-2.5, 0.0, 2.5]
# Its leading edges, lit gold (edges of WING, from point i to the next).
LEADING = [0, 1, 2, 4, 16, 18, 19, 20]
# The molten seams cracking across the right wing's top, `[x, z]` from and to.
SEAMS = [
    [
        [12.0, 8.0],
        [30.0, 1.0],
    ],
    [
        [30.0, 1.0],
        [44.0, -16.0],
    ],
    [
        [22.0, -6.0],
        [26.0, -30.0],
    ],
    [
        [30.0, 1.0],
        [40.0, 6.0],
    ],
]

# The spire over the core (lathe profile), rising through the ring's hub to its lit crown.
SPIRE = [
    [6.0, 0.0],
    [5.0, 6.0],
    [2.6, 12.0],
]
SPIRE_BASE = 9
CROWN = [
    [2.4, 0.0],
    [0.0, EMBER_CROWN[2] - SPIRE_BASE - 12.0],
]

# The ring: its rim (lathe profile), the hub round the spire and its spokes.
ORBIT = EMBER_LANCE.orbit
RIM = [
    [ORBIT - 2.6, 8.6],
    [ORBIT + 2.6, 8.6],
    [ORBIT + 3.2, 9.6],
    [ORBIT + 2.0, 10.4],
    [ORBIT - 2.0, 10.4],
    [ORBIT - 2.6, 8.6],
]
HUB = [
    [6.5, 11.0],
    [8.6, 11.0],
    [9.0, 12.6],
    [6.5, 13.2],
    [6.5, 11.0],
]
SPOKE = [
    [-1.8, 8.0],
    [1.8, 8.0],
    [1.2, ORBIT - 2.0],
    [-1.2, ORBIT - 2.0],
]


def _along_nose(x: float, y: float, z: float, dz: float) -> Any:
    """Return a placement at `[x, y, z - dz]`, lying along Z (`{ at, pitch: QUARTER }`)."""
    return Placement([x, y, z - dz], 0, QUARTER)


def _draw_fuselage(p: Any) -> None:
    """Draw the fuselage, its tail flattened to a deck under its plating (`draw_plating`).

    Soot-black on the deck behind its canopy, reactors aft; gold strips run down its flanks, and
    its ribs arch over the deck under the dome.
    """
    neon = p.neon
    canopy: Any = canopy_paint(CANOPY_BANDS, H.dark)

    def paint(side: int, band: int) -> Any:
        # Soot over its back behind the canopy, from the reactors' heat.
        painted: Any = canopy(side, band)
        if painted == None:
            if band < SOOT_BANDS and side in BACK:
                return SKIN.dark
            return None
        return painted

    p.flesh.loft(FIGHTER_SECTION, FUSELAGE, SKIN.base, None, LoftOptions(False, paint))
    back_ribs(p, [-26, -18, 18], RibSpec(8.5, 2, 7, 0.7))
    glands(p, [[0, 9.6, 24]], 1.4, HEAT["molten"])
    for s in SIDES:
        neon.box([0.5, 0.5, 26], GOLD, Placement([s * 9.4, 4, 8], s * 0.07))
        neon.box([0.5, 0.4, 16], HEAT["molten"], Placement([s * 4.6, 7.4, 38], -s * 0.1))
    reactor_sacs(
        p,
        [
            [4, 3.6, -55],
            [-4, 3.6, -55],
        ],
        3,
        HEAT["molten"],
    )
    reactor_sacs(
        p,
        [
            [11, 2.4, -50],
            [-11, 2.4, -50],
        ],
        2.2,
        GOLD,
    )


def _draw_wings(p: Any) -> None:
    """Draw the spiky wings: soot-dark tops cracked with molten seams.

    They have gold leading edges and spikes.
    """
    neon = p.neon
    p.flesh.bevel_slab(WING, WING_Y, [0.6, 0.8], SKIN.dark, None, SKIN.base)
    edge_lights(neon, WING, LEADING, [-1.2, -0.2], GOLD)
    for s in SIDES:
        magma_vein(
            p,
            [
                [s * 10, 2.7, 0],
                [s * 30, 2.7, -6],
                [s * 48, 2.6, -18],
            ],
            0.8,
            GOLD,
        )
        for pair in SEAMS:
            a = pair[0]
            b = pair[1]
            dx = s * (b[0] - a[0])
            dz = b[1] - a[1]
            neon.box(
                [0.7, 0.3, hypot2(dx, dz)],
                HEAT["molten"],
                Placement(
                    [(s * (a[0] + b[0])) / 2, WING_Y[2], (a[1] + b[1]) / 2],
                    math.atan2(dx, dz),
                ),
            )
        spike(p, [s * 52, WING_Y[2] - 0.5, -21], [QUARTER + 0.15, 0, math.pi - s * 0.6], [1.6, 9])
        spike(p, [s * 46, WING_Y[2] - 0.5, 11], [QUARTER - 0.1, 0, s * 0.9], [1.4, 7])
        spike(p, [s * 28, WING_Y[2] - 0.5, -42], [QUARTER, 0, math.pi - s * 0.25], [1.3, 6])
        p.flesh.box(
            [1, 7, 12],
            SKIN.dark,
            Placement([s * 12, 4, -36], 0, 0, s * 0.45),
            SKIN.bone,
        )
        neon.box([0.5, 0.5, 10], GOLD, Placement([s * 15, 10.2, -36], 0, 0, s * 0.45))


def _draw_nose_guns(p: Any) -> None:
    """Draw the twin ember cannons under the nose, their tips at the design's muzzles."""
    hull = p.hull
    charge = p.charge
    muzzle = p.muzzle
    for m in EMBER_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(1.5, 15, 6, H.dark, _along_nose(x, y, z, 18), 1.1)
        hull.cylinder(2.3, 5, 6, SHADE["edge"], _along_nose(x, y, z, 20))
        charge.cylinder(1.2, 3, 6, WHITE, _along_nose(x, y, z, 3), 0.5)
        muzzle([x, y, z])


def _draw_spire(p: Any) -> None:
    """Draw the spire over the core, its crown glowing where its spirals leave from."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    hull.lathe(SPIRE, 6, H.panel, Placement([0, SPIRE_BASE, 0]))
    neon.ring(5.4, 0.8, 6, GOLD, Placement([0, SPIRE_BASE + 5, 0]))
    charge.lathe(CROWN, 6, WHITE, Placement([0, SPIRE_BASE + 12, 0]))
    muzzle(boss_point(EMBER_CROWN[0], EMBER_CROWN[1], EMBER_CROWN[2]), "ring")


def _draw_core(p: Any) -> None:
    """Draw the core body: fuselage, wings, nose guns, spire and the embers on it.

    The dorsal spikes are on its back plating (`draw_plating`).
    """
    _draw_fuselage(p)
    _draw_wings(p)
    _draw_nose_guns(p)
    _draw_spire(p)
    embers(p.neon)


def _draw_ring(p: Any) -> None:
    """Draw the turning ring (MB-EMBER-HERALD-03, MB-EMBER-HERALD-06).

    A soot-black rim lit gold, held by three spokes from the hub.
    """
    hull = p.hull
    neon = p.neon
    r = ORBIT
    hull.lathe(RIM, 18, H.base, None, False)
    hull.ring(r + 1.6, 0.3, 18, HEAT["soot"], Placement([0, 10.4, 0]))
    neon.ring(r + 3.3, 0.7, 18, GOLD, Placement([0, 8.8, 0]))
    neon.ring(r - 2.7, 0.5, 18, HEAT["molten"], Placement([0, 9, 0]))
    hull.lathe(HUB, 8, H.panel, None, False)
    neon.ring(9.1, 0.5, 8, GOLD, Placement([0, 11.6, 0]))
    for a in around(3):
        yaw = a + math.pi / 3
        hull.bevel_slab(
            SPOKE, [10, 10.6, 11.4], [0.2, 0.5], H.panel, Placement(None, yaw), HEAT["soot"]
        )


def _gun_muzzles(part_id: str) -> list[Any]:
    """`EMBER_HERALD.guns[part.id]?.gun ?? []`."""
    entry: Any = EMBER_HERALD.guns[part_id]
    if entry == None or entry.gun == None:
        return []
    guns: list[Any] = entry.gun
    return guns


def _lance_part(muzzles: list[Any]) -> Any:
    """Return a lance on the ring (MB-EMBER-HERALD-03).

    It is drawn from its design's muzzles (`muzzles`).
    """

    def draw(parts: Any, at: Vec3) -> None:
        ember_lance(parts, muzzles, at)

    return draw


def build_ember_herald(scene: Any) -> Any:
    """Build the Ember Herald (MB-EMBER-HERALD-01, MB-EMBER-HERALD-04).

    A fast, spiky interceptor (3.5 L) wreathed in embers, gold neon: spiked wings cracked with
    molten seams, a spire over the core, and a ring turning over it carrying three ember lances.
    """
    lances = {}
    for part in EMBER_HERALD.stats.parts:
        if part.reveal != None:
            continue  # A hidden weapon, drawn from its look (`hidden_weapon_shapes`).
        lances[part.id] = _lance_part(_gun_muzzles(part.id))
    return build_boss_model(
        EMBER_HERALD,
        scene,
        GOLD,
        {
            "core": _draw_core,
            "ring": _draw_ring,
            "parts": lances,
            "armour": {"back": {"whole": draw_plating}},
        },
    )
