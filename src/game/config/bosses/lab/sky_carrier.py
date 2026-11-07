# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-11 final boss, the Sky Carrier (specs/bosses/lab/L-11-sky-carrier.md).

Lab boss: in the dev viewer only (no level brings it in). A flying aircraft carrier seen from
above: a long flat flight deck with its markings, two catapults down its bow, an island tower on
its right edge, ducted lift engines on sponsons along its hull. It fights with its deck guns and its
aircraft: the catapults launch Hornets that dive at the player, the island's fire-control laser
tracks the player. At its first transformation the middle of its flight deck splits down the centre
line and its two halves slide apart sideways (it changes shape, BOSS-45), opening the hangar below:
a hangar launching more Hornets and a pair of mortars rise out of it (swarm and flak). At its second
the island tower folds down outboard and retires (BOSS-45, BOSS-46), the plating of its bow quarters
bursts off on a pair of gatlings, and a giant beam cannon stowed on its foredeck swings forward over
the bow on its boom (a rig, BOSS-46).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide, swing
from game.config.bosses.weapon_kinds import BEAM
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-SKY-CARRIER-01: the flight deck's outline (its right half, bow to stern; mirrored), its
# underside and its top.
DECK = [[0, -98], [9, -95], [20, -84], [26, -70], [26, 62], [22, 70], [0, 70]]  # type: list[list[float]]
DECK_LOW = 12
DECK_TOP = 15
# The hull under it (FB-SKY-CARRIER-02): half width, bow and stern, keel and top.
HULL_HALF = 19
HULL_ENDS = [-88, 64]
HULL_LOW = 2
# The split deck (FB-SKY-CARRIER-05): the right half of the middle of the deck, `[y0, y1]`, and
# how far each half slides out sideways; the hangar's floor under it.
SPLIT = [-48, -4]
SPLIT_OUT = 17
HANGAR_FLOOR = 5
# The island tower on the right edge (FB-SKY-CARRIER-02): `[x0, x1, y0, y1]`, its bridge's top
# and its mast's top. It folds down outboard about its outer foot (FB-SKY-CARRIER-11).
ISLAND = [21, 33, 8, 36]
ISLAND_TOP = 37
MAST_TOP = 47
# The catapults down the bow (FB-SKY-CARRIER-02): their tracks' X and `[y0, y1]`.
CATAPULT_X = 9
CATAPULT_Y = [-94, -52]
# The lift engines (FB-SKY-CARRIER-02): ducted fans on sponsons out from the hull, `[x, y]` (the
# right side has none where the island folds down), their duct's radius and height.
LIFT_FANS = [[-33, -62], [-33, 6], [-33, 48], [33, -62], [33, 48]]
FAN_RADIUS = 7
FAN_H = 8
# The beam boom (FB-SKY-CARRIER-11): hinged at the bow's tip, stowed lying aft along the deck's
# centre line between the catapults, it swings forward over the bow; its hinge's Y and height,
# and its length to the emitter.
BOOM_HINGE = [-96, DECK_TOP + 1.5]
BOOM_LENGTH = 22
# The beam cannon's emitter stands on the boom's end, on its top.
BEAM_H = BOOM_HINGE[1] + 1.4

GOLD = bullet("orange", 180)
RED = bullet("red", 190)
MAGENTA = bullet("magenta", 175)


def fpart(part_id: str, at: list[Any], radius: float, health: float, more: Any = None) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    options: Any = {"drop": 0.6}
    if more != None:
        options = merge(options, more)
    return part(part_id, at, radius, health, options)


# The guns (BOSS-58, FB-SKY-CARRIER-03): twin barrels on each deck gun's turret, the island's laser
# turret on its roof, and the core's on the after deck: a three-barrelled turret and a rotor behind
# it, under a hatch until its last stage. The catapults launch Hornets and have no gun.
DECK_GUN_AT = [17, -26]
DECK_GUN = {"size": 4.6, "barrels": 2, "gap": 3, "bore": 1.1, "length": 7.5}
CATAPULT_AT = [CATAPULT_X, -66]
ISLAND_AT = [27, 20]
ISLAND_LASER_AT = [27, 15]
ISLAND_LASER = {"size": 4.4, "bore": 1.8, "length": 9, "turret": True}
STERN_GUN_AT = [0, 44]
STERN_GUN = {"size": 5.5, "barrels": 3, "gap": 1.2, "bore": 1.2, "length": 8}
ROTOR_AT = [0, 58]
ROTOR = {"size": 5, "barrels": 14, "layout": "ring", "bore": 0.75, "length": 3.6}
GUN_H = DECK_TOP + 1

_SKY_CARRIER = record({
    "id": "sky-carrier",
    # Its points, its core's drop and its parts' drops (FB-SKY-CARRIER-13).
    "stats": stats({
        "id": "sky-carrier",
        "name": "Sky Carrier",
        "size": 5,
        "coreRadius": 20,
        "coreHealth": 1700,
        "points": 9000,
        "groundSpeed": 0.5,
        "coreDrop": 1,
        "parts": [
            fpart("deck-left", [-DECK_GUN_AT[0], DECK_GUN_AT[1]], 10, 820),
            fpart("deck-right", DECK_GUN_AT, 10, 820),
            fpart("catapult-left", [-CATAPULT_AT[0], CATAPULT_AT[1]], 9, 760),
            fpart("catapult-right", CATAPULT_AT, 9, 760),
            # D-228: it leaves the fight as the island folds down; the beam takes over from it.
            fpart("island", ISLAND_AT, 10, 900, {"retire": 2}),
        ],
    }),
    # Where it stops and how it moves in place (FB-SKY-CARRIER-06): a long, heavy ship, slow sways.
    "stopFraction": 0.7,
    "sway": {"amplitude": 32, "period": 10},
    "bob": {"amplitude": 5, "period": 5},
    # Its catapults' Hornets (BOSS-25): two at a time, side by side, diving at the player.
    "launches": [
        {"from": "catapult-left", "kind": "hornets", "count": 2, "every": 8, "first": 3},
        {"from": "catapult-right", "kind": "hornets", "count": 2, "every": 8, "first": 7},
    ],
    "guns": {},
    # Its gun mounts (BOSS-58, FB-SKY-CARRIER-03).
    "mounts": [
        gun_mount("deck-left", "deck-left", [-DECK_GUN_AT[0], DECK_GUN_AT[1]], GUN_H, DECK_GUN),
        gun_mount("deck-right", "deck-right", DECK_GUN_AT, GUN_H, DECK_GUN),
        laser_mount("island", "island", ISLAND_LASER_AT, ISLAND_TOP + 0.5, ISLAND_LASER),
        gun_mount("stern-gun", "core", STERN_GUN_AT, GUN_H, STERN_GUN),
        gun_mount("stern-rotor", "core", ROTOR_AT, GUN_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-SKY-CARRIER-08): the deck guns'
    # aimed pairs and the island's tracking laser; the core's aimed shots and spreads, then fans
    # 12° apart (BOSS-58), ending in the stern rotor's spiral.
    "stages": stages(
        [
            volley.aimed("deck-left", 2.0, 2, 6, RED, 0.8),
            volley.aimed("deck-right", 2.0, 2, 6, RED, 1.8),
            volley.laser("island", 7.5, 1.4, 3),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, GOLD, 1.4)],
            [volley.aimed("core", 2.6, 3, 8, GOLD, 1)],
            [volley.fan("core", 2.6, 5, 12, GOLD, 0.8)],
            [
                volley.burst("core", 2.4, 4, 0.13, RED, 0.6),
                volley.fan("core", 3, 3, 12, GOLD, 1.6),
            ],
            [
                volley.fan("core", 2.4, 7, 12, GOLD, 0.6),
                volley.aimed("core", 2.8, 1, 0, RED, 1.5),
            ],
            [
                volley.ring("core", 1.4, 14, 9, MAGENTA, 0.4),
                volley.fan("core", 2.8, 5, 12, GOLD, 1.2),
            ],
        ],
    ),
})


def bow_beam(
    part_id: str, at: list[Any], radius: float, health: float, reveal: int, first: float
) -> Any:
    """Return a beam cannon at the end of the boom the carrier swings out over its bow (BOSS-46).

    As `hidden_weapons.tail_cannon` (D-228), but at its bow, pointing down the screen (its emitter
    on its boom's end): a giant laser at the player. Its look is a `beam` on a `rig`: the boss
    model draws it, and it comes out of no armour region.
    """
    height = BEAM_H
    emitter = laser_mount(
        part_id,
        part_id,
        at,
        height,
        {"size": radius * 0.55, "bore": radius * 0.3, "length": radius * 0.9},
    )
    return record({
        "part": part(part_id, at, radius, health, {"reveal": reveal, "drop": 0.3}),
        "mounts": [emitter],
        "look": {"kind": "beam", "radius": radius, "height": height, "rig": True},
        "volleys": [volley.laser(part_id, BEAM.every, BEAM.firing, first, BEAM.width)],
        "launches": [],
    })


# Where the hidden weapons stand: the hangar on the centre line and the mortars ahead of it on the
# hangar's floor (FB-SKY-CARRIER-10); the gatlings on the bow quarters, the beam at the end of its
# boom swung forward (FB-SKY-CARRIER-11).
HANGAR_AT = [0, -24]
MORTAR_AT = [9, -40]
GATLING_AT = [18, -72]
BEAM_AT = [0, BOOM_HINGE[0] - BOOM_LENGTH]
# The bow quarters' plating (the right one; mirrored).
BOW_PLATING = [[12, -61], [26, -61], [26, -70], [21, -81], [12, -81]]
PLATING_TOP = DECK_TOP + 2.5


def _split_half() -> list[list[float]]:
    """Return the right half of the split deck's outline (from the centre line out)."""
    return [[0, SPLIT[0]], [DECK[3][0], SPLIT[0]], [DECK[3][0], SPLIT[1]], [0, SPLIT[1]]]


def _island() -> list[list[float]]:
    """Return the island tower's outline."""
    return [
        [ISLAND[0], ISLAND[2]],
        [ISLAND[1], ISLAND[2]],
        [ISLAND[1], ISLAND[3]],
        [ISLAND[0], ISLAND[3]],
    ]


# FB-SKY-CARRIER-05: each deck half slides straight out sideways; the island swings 90° outboard
# about its outer foot, along the ship, to lie on its side over the rail.
DECK_SLIDE = slide([[0, 0, 0], [SPLIT_OUT, 0, 0]])
ISLAND_FOLD = swing([ISLAND[1], (ISLAND[2] + ISLAND[3]) / 2, DECK_TOP], "along", [0, 90])

# Its transformations: once both deck guns are gone the middle of its deck splits and slides apart,
# a hangar and a pair of mortars rising out of the hangar below; once both catapults are gone its
# island folds down outboard (its laser retires), its bow quarters' plating bursts off on a pair of
# gatlings and the beam cannon swings forward over the bow. The hatch over the stern rotor bursts as
# the rotor comes into use, in its last stage (BOSS-58).
SKY_CARRIER = with_weapons(
    merge(
        _SKY_CARRIER,
        {
            "transformParts": [
                ["deck-left", "deck-right"],
                ["catapult-left", "catapult-right"],
            ]
        },
    ),
    [
        hidden_weapon("hangar", "hangar", HANGAR_AT, 10, 720, 1, "orange", 1.6, [HANGAR_FLOOR, 11]),
        hidden_weapon(
            "mortar-left",
            "mortar",
            [-MORTAR_AT[0], MORTAR_AT[1]],
            6.5,
            720,
            1,
            "orange",
            1.2,
            [HANGAR_FLOOR, HANGAR_FLOOR + 3],
        ),
        hidden_weapon(
            "mortar-right",
            "mortar",
            MORTAR_AT,
            6.5,
            720,
            1,
            "orange",
            2.0,
            [HANGAR_FLOOR, HANGAR_FLOOR + 3],
        ),
        bow_beam("beam", BEAM_AT, 12, 900, 2, 1.4),
        hidden_weapon(
            "gatling-left",
            "gatling",
            [-GATLING_AT[0], GATLING_AT[1]],
            7,
            900,
            2,
            "red",
            1.2,
            [DECK_TOP, PLATING_TOP],
        ),
        hidden_weapon(
            "gatling-right", "gatling", GATLING_AT, 7, 900, 2, "red", 2.0, [DECK_TOP, PLATING_TOP]
        ),
    ],
    concat(
        concat(
            moving_region("deck", 1, _split_half(), DECK_SLIDE, None, [DECK_LOW - 0.5, 1000]),
            moving_region("island", 2, _island(), ISLAND_FOLD, None, [DECK_TOP - 0.5, 1000], False),
        ),
        [
            armour_region("bow-plating", 2, BOW_PLATING, "shell", [DECK_TOP - 0.5, PLATING_TOP]),
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 6.4 * math.cos(k * math.pi / 4 + math.pi / 8),
                        ROTOR_AT[1] + 6.4 * math.sin(k * math.pi / 4 + math.pi / 8),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "stern-rotor",
            ),
        ],
    ),
)
