# Copyright (c) 2026 Renaud Guillon
"""The Ice Queen (MB-ICE-QUEEN-01 to MB-ICE-QUEEN-06, 2-5).

Logical pixels, nose +Z (down the screen), Y up (towards the camera); +X is the screen's left.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_2.ice_queen import (
    ICE_QUEEN,
    ICE_QUEEN_NOSE_GUNS,
    ICE_QUEEN_SHARD,
    ICE_QUEEN_SPIRE,
)
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_greebles import plate, rect
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H
from game.view.bosses.overlord_city import edge_lights
from game.view.bosses.world_2.ice_queen_armour import draw_plating, plating_pieces
from game.view.bosses.world_2.ice_queen_details import draw_details
from game.view.bosses.world_2.ice_queen_shards import (
    FROST,
    PALE_BLUE,
    VIOLET,
    crystal,
    ice_shard,
    icicles,
)
from game.view.bosses.world_2.w2_organic import (
    ICE_FLESH,
    deck_section,
    sinew,
)
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, SIDES, around, flip_x
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import RibSpec, organ, ribs
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts

# __pragma__ ("noskip")


# The fuselage, long and slender: its rear flattened into a deck at `DECK` (`FLAT` of the way up
# its stations), where the plating it sheds lies (MB-ICE-QUEEN-07, `ice_queen_armour`); its front
# rising from the deck and closing to a needle nose (loft stations, tail to nose).
DECK = 5.5
FLAT = 0.62
REAR_SECTION = deck_section(FLAT)


def rear_station(z: float, half_width: float, bottom: float) -> list[float]:
    """Return a loft station of the rear whose flat deck lies at `DECK`."""
    return [z, half_width, bottom, bottom + (DECK - bottom) / FLAT]


REAR = [
    rear_station(-56, 5, 0),
    rear_station(-40, 8, -0.5),
    rear_station(-10, 10, -1),
]
FRONT = [  # type: list[list[float]]
    [-10, 10, -1, DECK + 0.1],
    [-2, 10, -1, 9.5],
    [20, 8, -0.5, 8.5],
    [42, 4.5, 0, 6],
    [58, 0, 2.5, 2.5],
]
# The fuselage's back (sides of the section), snowed over on the rear deck.
BACK = [3, 4]
CANOPY = [2, 3, 4, 5]

# The right wing (+X), swept far back from the fuselage, and a canard at the nose.
WING = [  # type: list[list[float]]
    [7, 18],
    [46, -24],
    [47.5, -31],
    [41, -34],
    [7, -27],
]
CANARD = [  # type: list[list[float]]
    [4, 36],
    [15, 25],
    [15.5, 22],
    [4, 26],
]
WING_TOP = 2.4

# The crystal spire over the core (a lathe profile) and the charge light at its tip.
SPIRE = [  # type: list[list[float]]
    [5.5, 0],
    [4.6, 5],
    [2.6, 11],
    [0, 13.6],
]
SPIRE_BASE = 9
SPIRE_TIP = [
    [1.3, 0],
    [0, ICE_QUEEN_SPIRE[2] - SPIRE_BASE - 13.2],
]

# The crown ring: its rim (lathe profile), the hub round the spire and three spokes.
RIM = [  # type: list[list[float]]
    [39.5, 10],
    [44, 10],
    [44.6, 11],
    [43.2, 12],
    [40.2, 12],
    [39.5, 10],
]
HUB = [  # type: list[list[float]]
    [5.5, 12.5],
    [7.5, 12.5],
    [7.8, 14],
    [5.5, 14.6],
    [5.5, 12.5],
]
SPOKE = [  # type: list[list[float]]
    [-1.6, 7],
    [1.6, 7],
    [1, 40],
    [-1, 40],
]


# The loft bands of the fuselage's front: the canopy's band and the band past it (the needle
# nose).
CANOPY_BAND = 2
NOSE_BAND = 3


def front_paint(side: int, band: int) -> Any:
    """Return the canopy's seam and the nose's bone on the fuselage's front."""
    if band == CANOPY_BAND and side in CANOPY:
        return ICE_FLESH.seam
    if band == NOSE_BAND:
        return ICE_FLESH.bone
    return None


def rear_paint(side: int, _band: int) -> Any:
    """Return the rimed back of the fuselage's rear deck."""
    return ICE_FLESH.rime if side in BACK else None


def draw_fuselage(p: EnemyParts) -> None:
    """Draw the fuselage (its rear a flat deck under the plating), and the reactors at its tail.

    The glands of the rear are on its plating (`draw_plating`).
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # MB-ICE-QUEEN-02: a slender body of violet flesh, ribbed, closing to a bone needle at the nose.
    flesh.loft(REAR_SECTION, REAR, ICE_FLESH.graphite, None, LoftOptions(False, rear_paint))
    flesh.loft(FIGHTER_SECTION, FRONT, ICE_FLESH.graphite, None, LoftOptions(False, front_paint))
    for s in SIDES:
        neon.box([0.5, 0.5, 30], PALE_BLUE, Placement([s * 8.6, 4.5, 2], s * 0.06))
        neon.box([0.5, 0.4, 18], VIOLET, Placement([s * 5.2, 6.4, 33], -s * 0.12))
        reactor_sac(p, [s * 3.6, 3.4, -57], 2.8, PALE_BLUE, ICE_FLESH.membrane, 5)
        p.reactor([s * 12.5, 2.6, -53], 2.2)
    ribs(
        flesh,
        [-40, -32, -24, -16],
        RibSpec(8.5, 3, 6.5, 0.6),
        ICE_FLESH.bone,
    )
    plate(hull, rect(8, 10), [9.6, 0.5], H.panel, Placement([0, 0, 8]))


def draw_wings(p: EnemyParts) -> None:
    """Draw the swept wings and canards.

    Frosted tops, violet leading edges, crystals at the tips.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        # MB-ICE-QUEEN-02: swept membrane wings stretched on bone struts, too long to flutter.
        if s > 0:
            wing: Any = WING
            canard: Any = CANARD
        else:
            wing = flip_x(WING)
            canard = flip_x(CANARD)
        flesh.bevel_slab(
            wing,
            [0, 1.2, WING_TOP],
            [0.6, 1.4],
            ICE_FLESH.membrane,
            None,
            ICE_FLESH.graphite,
        )
        sinew(flesh, [s * 7, WING_TOP, 14], [s * 46, WING_TOP, -28], 1, ICE_FLESH.bone, [0, 0.8, 6])
        sinew(
            flesh, [s * 8, WING_TOP, 4], [s * 30, WING_TOP, -30], 0.8, ICE_FLESH.bone, [0, 0.6, 2]
        )
        edge_lights(neon, wing, [0], [0.6, 1.6], VIOLET)
        edge_lights(neon, wing, [1], [0.6, 1.6], PALE_BLUE)
        hull.bevel_slab(canard, [1.5, 2.4, 3.4], [0.3, 0.8], H.panel, None, FROST.frosted)
        edge_lights(neon, canard, [0], [2, 3], VIOLET)
        crystal(flesh, [s * 44, WING_TOP, -29], [0, -0.35 * s, 0], [2.6, 9])
        crystal(flesh, [s * 26, WING_TOP, -20], [0, 0.4 * s, 0.3], [1.6, 5])
        icicles(
            flesh,
            s,
            [
                [12, -27.5],
                [20, -29],
                [28, -30.5],
                [36, -32],
            ],
        )


def draw_nose_guns(p: EnemyParts) -> None:
    """Draw the twin crystal cannons by the nose (MB-ICE-QUEEN-03).

    Their tips are at the design's muzzles.
    """
    hull = p.hull
    charge = p.charge
    muzzle = p.muzzle
    for m in ICE_QUEEN_NOSE_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(1.6, 14, 6, H.dark, Placement([x, y, z - 17], 0, QUARTER), 1.2)
        hull.cylinder(2.2, 5, 6, H.panel, Placement([x, y, z - 19], 0, QUARTER))
        charge.cylinder(1.3, 3, 6, WHITE, Placement([x, y, z - 3], 0, QUARTER), 0.5)
        muzzle(tip, "gun")


def draw_spire(p: EnemyParts) -> None:
    """Draw the crystal spire over the core (MB-ICE-QUEEN-03).

    It glows at its tip, where its spiral leaves from.
    """
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    # MB-ICE-QUEEN-02: the spire is a crystal grown out of a swollen gland on the back.
    organ(flesh, 7, 6, ICE_FLESH.membrane, Placement([0, 4, 0]), 0.45)
    flesh.lathe(SPIRE, 6, FROST.ice, Placement([0, SPIRE_BASE, 0]))
    neon.ring(5.7, 0.7, 6, VIOLET, Placement([0, SPIRE_BASE + 0.4, 0]))
    charge.lathe(SPIRE_TIP, 6, WHITE, Placement([0, SPIRE_BASE + 13.2, 0]))
    muzzle(
        boss_point(ICE_QUEEN_SPIRE[0], ICE_QUEEN_SPIRE[1], ICE_QUEEN_SPIRE[2]),
        "ring",
    )


def draw_core(p: EnemyParts) -> None:
    """Draw the core body: fuselage, wings, nose guns and spire."""
    draw_fuselage(p)
    draw_wings(p)
    draw_nose_guns(p)
    draw_spire(p)
    draw_details(p)


def draw_ring(p: EnemyParts) -> None:
    """Draw the crown ring (MB-ICE-QUEEN-03; it turns, MB-ICE-QUEEN-06).

    A frosted rim lit violet, held by three spokes from the hub.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # MB-ICE-QUEEN-03: a crown of bone and sinew around the body, metal only at its hub.
    flesh.lathe(RIM, 18, ICE_FLESH.sinew, None, False)
    flesh.ring(43.4, 0.25, 18, ICE_FLESH.bone, Placement([0, 12, 0]))
    neon.ring(44.8, 0.7, 18, VIOLET, Placement([0, 10.2, 0]))
    neon.ring(39.3, 0.6, 18, PALE_BLUE, Placement([0, 10.4, 0]))
    hull.lathe(HUB, 8, H.panel, None, False)
    neon.ring(7.9, 0.5, 8, PALE_BLUE, Placement([0, 13, 0]))
    for a in around(3):
        yaw = a + math.pi / 3
        flesh.bevel_slab(
            SPOKE,
            [12, 12.6, 13.4],
            [0.2, 0.5],
            ICE_FLESH.bone,
            Placement(None, yaw),
            ICE_FLESH.rime,
        )
        x = math.sin(yaw) * 42
        z = math.cos(yaw) * 42
        crystal(flesh, [x, 11.5, z], [0.5, 0, yaw], [1.8, 7])


def keyed(names: list[str], drawings: list[Any]) -> Any:
    """`Object.fromEntries`: a plain object from parallel lists of keys and values."""
    result: Any = None
    __pragma__("skip")
    result = record(dict(zip(names, drawings, strict=False)))
    __pragma__("noskip")
    __pragma__(
        "js",
        "{}",
        """
    result = {};
    for (let i = 0; i < names.length; i++) {
        result[names[i]] = drawings[i];
    }
    """,
    )
    return result


def shard_part(part_id: str) -> Any:
    """Return the drawing of the crown shard `part_id`: its muzzles from the design.

    It is a factory, so each shard keeps its own id.
    """

    def draw(parts: EnemyParts, _at: Any = None) -> None:
        # Drawn in model space: the point the part sits at (handed to every part) is not used.
        gun = ICE_QUEEN.guns[part_id]
        muzzles = []
        if gun != None and gun.gun != None:
            muzzles = gun.gun
        ice_shard(parts, muzzles, ICE_QUEEN_SHARD.height)

    return draw


def shard_parts() -> Any:
    """Return the crown shards, one drawing per part of the design, by part id."""
    names: list[str] = []
    drawings: list[Any] = []
    for part in ICE_QUEEN.stats.parts:
        if part.reveal != None:
            continue  # A hidden weapon, drawn from its look (`hidden_weapon_shapes`).
        names.append(part.id)
        drawings.append(shard_part(part.id))
    return keyed(names, drawings)


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """Return the `BossDrawing` of a boss model: what the model is drawn from, with its armour."""
    return record({
        "core": core,
        "parts": parts,
        "turrets": turrets,
        "limbs": limbs,
        "ring": ring,
        "armour": {"back": {"whole": draw_plating, "pieces": plating_pieces()}},
    })


def build_ice_queen(scene: Any) -> BuiltEnemyModel:
    """MB-ICE-QUEEN-01, MB-ICE-QUEEN-04: the Ice Queen, a slender crystal interceptor (3.5 L).

    It has pale blue and violet neon: swept frosted wings, a crystal spire over the core, and a
    crown ring turning over it carrying three crystal shards. MB-ICE-QUEEN-02: now a living
    ice-wraith of violet flesh, membrane wings on bone and crystals grown through it, its crown of
    bone carrying three crystals grown from flesh sacs. The plating over its rear is the armour it
    sheds (MB-ICE-QUEEN-07).
    """
    return build_boss_model(
        ICE_QUEEN,
        scene,
        PALE_BLUE,
        boss_drawing(draw_core, shard_parts(), None, None, draw_ring),
    )
