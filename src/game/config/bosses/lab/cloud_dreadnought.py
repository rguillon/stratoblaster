# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-12 final boss, the Cloud Dreadnought (specs/bosses/lab/L-12-cloud-dreadnought.md).

Lab boss: in the dev viewer only (no level brings it in). A long flying battleship seen from above:
a sharp hull, a stepped bridge superstructure and two raked smokestacks on its centre line, a
triple-gun main turret fore and aft, a lift-engine nacelle out on each flank. Once both lift
engines are gone, the armour belts along its flanks swing out like wings (it changes shape,
BOSS-45), a battery riding each; once both main turrets are gone it turns broadside (BOSS-46), its
whole length across the screen, and the plating of its after deck bursts off on a pair of missile
racks and a lance: its starboard casemates open up, a wall of fire across the screen.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, only_while, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-CLOUD-DREADNOUGHT-01: the hull's half width along its length, `[y, half width]` from its bow
# (a point) to its stern (a flat transom), its deck's height and its keel's depth.
HULL = [  # type: list[list[float]]
    [-88, 0],
    [-76, 6],
    [-62, 11],
    [-46, 15],
    [-30, 17.5],
    [-12, 18],
    [20, 18],
    [40, 16.5],
    [56, 14],
    [68, 11],
    [76, 8],
]
DECK = 8
KEEL = -7

# The main turrets (FB-CLOUD-DREADNOUGHT-03): their barbettes' centres, radius and top; three heavy
# barrels each.
FORE_AT = [0, -50]
AFT_AT = [0, 52]
BARBETTE_RADIUS = 8.5
BARBETTE_TOP = 12
MAIN_GUN = {"size": 6.5, "barrels": 3, "gap": 2.4, "bore": 1.3, "length": 10}
# The superstructure: its two tiers `[half width, front, back, top]` (the hull's, they stay), the
# bridge on them (the part: a conning tower `[half width, front, back, top]` and its mast) and its
# flak rotor on the upper tier's back.
BRIDGE_AT = [0, -28]
SUPERSTRUCTURE = [[11, -40, -15, 15], [8, -37, -17, 21]]  # type: list[list[float]]
CONNING = [5.5, -37, -29, 27]
BRIDGE_ROTOR_AT = [0, -21.5]
BRIDGE_ROTOR = {"size": 4.2, "barrels": 8, "layout": "ring", "bore": 0.9, "length": 3.2}
# The lift engines (FB-CLOUD-DREADNOUGHT-03): a ducted lift fan out on each flank, on a pylon from
# the deck's edge; the pylon's twin AA turret at its root, on the deck.
ENGINE_AT = [29, 32]
ENGINE_RADIUS = 8.5
ENGINE_GUN_AT = [14, 27]
ENGINE_GUN = {"size": 4, "barrels": 2, "gap": 1.2, "bore": 0.9, "length": 6}
# The core's guns: a twin turret on the deckhouse behind the bridge, its rotor (its last spiral)
# under a hatch on the stern deck, and its starboard casemates (FB-CLOUD-DREADNOUGHT-11): fixed
# triple barrels pointing out of its right flank, so that, broadside, they point at the player.
CORE_GUN_AT = [0, -9]
CORE_GUN_TOP = 13
CORE_GUN = {"size": 4.4, "barrels": 2, "gap": 1.2, "bore": 1.0, "length": 7}
ROTOR_AT = [0, 65]
CORE_ROTOR = {"size": 4.4, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.2}
CASEMATE_YS = [-42, -34, 40, 46]
CASEMATE_TOP = DECK + 0.4
CASEMATE = {
    "size": 3,
    "barrels": 3,
    "gap": 2.6,
    "bore": 0.9,
    "length": 5,
    "turret": False,
    "restDeg": -90,
}
# Its preset fans' heading (the batteries' and the core's late ones): 45° off straight down,
# towards the screen's right as it comes in; they turn with it, so that once broadside they rake
# the screen 45° to its left (FB-CLOUD-DREADNOUGHT-10, FB-CLOUD-DREADNOUGHT-11).
BATTERY_HEADING = 45
# The smokestacks: their centres on the centre line, radius and top.
FUNNELS = [[0, 0.5], [0, 9]]  # type: list[list[float]]
FUNNEL_RADIUS = 3.8
FUNNEL_TOP = 22


def half_width(y: float) -> float:
    """Return the hull's half width at `y` (linear between the `HULL` stations)."""
    if y <= HULL[0][0]:
        return 0
    for k in range(1, len(HULL)):
        a = HULL[k - 1]
        b = HULL[k]
        if y <= b[0]:
            return float(a[1] + (b[1] - a[1]) * (y - a[0]) / (b[0] - a[0]))
    return float(HULL[len(HULL) - 1][1])


def casemate_at(y: float) -> list[float]:
    """Return where the casemate at `y` stands: on its sponson, on the right flank."""
    return [half_width(y) - 1.2, y]


SHELL = bullet("orange", 160, 5)
RED = bullet("red", 185)
MAGENTA = bullet("magenta", 175)
FLAK = bullet("orange", 130, 5)
WALL = bullet("red", 170)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


# The broadside (FB-CLOUD-DREADNOUGHT-11), in its core's last two stages (it is broadside by the
# time it is in them, unless it lost its batteries first): once the lance is out, its casemates fire
# their three barrels at once, one after the other from bow to stern, as long as the lance stands.
BROADSIDE = [
    only_while(
        merge(volley.fan("core", 2.4, 3, 0, WALL, 0.5 + 0.2 * k), {"mount": "casemate-" + str(k)}),
        "lance",
    )
    for k in range(len(CASEMATE_YS))
]

_CLOUD_DREADNOUGHT = record({
    "id": "cloud-dreadnought",
    # Its points, its core's drop and its parts' drops (FB-CLOUD-DREADNOUGHT-13).
    "stats": stats({
        "id": "cloud-dreadnought",
        "name": "Cloud Dreadnought",
        "size": 5,
        "coreRadius": 16,
        "coreHealth": 1600,
        "points": 10000,
        "groundSpeed": 0.8,
        "coreDrop": 1,
        "parts": [
            fpart("engine-left", [-ENGINE_AT[0], ENGINE_AT[1]], 11, 700),
            fpart("engine-right", ENGINE_AT, 11, 700),
            fpart("turret-fore", FORE_AT, 11, 900),
            fpart("turret-aft", AFT_AT, 11, 900),
            fpart("bridge", BRIDGE_AT, 11, 850),
        ],
    }),
    # Where it stops and how it moves in place (FB-CLOUD-DREADNOUGHT-06): a heavy ship's slow
    # drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 40, "period": 10},
    "bob": {"amplitude": 4, "period": 4.6},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-CLOUD-DREADNOUGHT-03).
    "mounts": concat(
        [
            gun_mount(
                "engine-left",
                "engine-left",
                [-ENGINE_GUN_AT[0], ENGINE_GUN_AT[1]],
                DECK,
                ENGINE_GUN,
            ),
            gun_mount("engine-right", "engine-right", ENGINE_GUN_AT, DECK, ENGINE_GUN),
            gun_mount("turret-fore", "turret-fore", FORE_AT, BARBETTE_TOP, MAIN_GUN),
            gun_mount("turret-aft", "turret-aft", AFT_AT, BARBETTE_TOP, MAIN_GUN),
            gun_mount("bridge", "bridge", BRIDGE_ROTOR_AT, SUPERSTRUCTURE[1][3], BRIDGE_ROTOR),
            gun_mount("core-gun", "core", CORE_GUN_AT, CORE_GUN_TOP, CORE_GUN),
            gun_mount("core-rotor", "core", ROTOR_AT, DECK, CORE_ROTOR),
        ],
        [
            gun_mount(
                "casemate-" + str(k), "core", casemate_at(CASEMATE_YS[k]), CASEMATE_TOP, CASEMATE
            )
            for k in range(len(CASEMATE_YS))
        ],
    ),
    # Its parts' volleys, then the core's pattern per stage (FB-CLOUD-DREADNOUGHT-08): the lift
    # engines' AA turrets fire bursts, the main turrets sweep aimed spreads of three heavy shells
    # (fore and aft in turn), the bridge's flak rotor rings of 8; the core's twin turret adds a new
    # aimed pattern at each stage, then its rotor's spiral of 16. From stage 4 on (it may be
    # broadside by then) the core aims nothing: its turret sweeps fans `BATTERY_HEADING` off
    # straight down, which turn with it (a turret's aim at the player ignores its heading).
    "stages": stages(
        [
            volley.burst("engine-left", 2.6, 3, 0.13, RED, 1.0),
            volley.burst("engine-right", 2.6, 3, 0.13, RED, 2.3),
            volley.aimed("turret-fore", 2.8, 3, 8, SHELL, 1.6),
            volley.aimed("turret-aft", 2.8, 3, 8, SHELL, 3.0),
            volley.ring("bridge", 3.2, 8, 22.5, FLAK, 2.0),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, MAGENTA, 1.4)],
            [volley.burst("core", 2.6, 3, 0.14, MAGENTA, 0.8)],
            [volley.aimed("core", 2.2, 2, 6, MAGENTA, 0.8)],
            [
                volley.burst("core", 2.4, 4, 0.12, MAGENTA, 0.6),
                volley.aimed("core", 3.0, 1, 0, RED, 1.6),
            ],
            concat([volley.fan("core", 2.2, 7, 8, MAGENTA, 0.6, BATTERY_HEADING)], BROADSIDE),
            concat(
                [
                    volley.ring("core", 1.4, 16, 11.25, FLAK, 0.4),
                    volley.fan("core", 2.6, 5, 10, RED, 1.2, BATTERY_HEADING),
                ],
                BROADSIDE,
            ),
        ],
    ),
})

# FB-CLOUD-DREADNOUGHT-05: the right armour belt, as drawn (swung out flat like a wing at deck
# height, a swept trapezoid from its hinge along the deck's edge), and its swing about the boss's
# length through that hinge: at rest it hangs down along the hull's flank (90°); the left one is
# its mirror image.
BELT_ROOT = 18
BELT = [[BELT_ROOT, -24], [42, -12], [46, -5], [46, 10], [42, 15], [BELT_ROOT, 20]]
BELT_THICK = 2.5
BELT_SWING = swing([BELT_ROOT, 0, DECK], "along", [90, 0])
BELT_HEIGHTS = [DECK - BELT_THICK - 2.5, DECK + 0.5]
# Where the batteries ride on the belts once out (FB-CLOUD-DREADNOUGHT-10).
BATTERY_AT = [32, -1]
BATTERY_POD = [DECK, DECK + 3]
# The after deck's plating (FB-CLOUD-DREADNOUGHT-11): `[x0, x1, y0, y1]` and its top; the racks
# and the lance under it.
PLATING = [-12.5, 12.5, 14, 38]
PLATING_TOP = DECK + 2.5
RACK_AT = [7, 21]
LANCE_AT = [0, 31.5]
WEAPON_POD = [DECK, DECK + 3]

# How far it turns at each transformation (BOSS-46): not at its first; a quarter turn clockwise at
# its second, its nose to the screen's left and its right flank to the player.
TURNS = [0, math.pi / 2]


def _battery(part_id: str, at: list[Any], first: float) -> Any:
    """Return a battery whose fans go `BATTERY_HEADING` off straight down (see above)."""
    weapon = hidden_weapon(part_id, "battery", at, 9, 720, 1, "red", first, BATTERY_POD)
    volleys = [
        merge(v, {"shape": merge(v.shape, {"headingDeg": BATTERY_HEADING})}) for v in weapon.volleys
    ]
    return merge(weapon, {"volleys": volleys})


def _lance(part_id: str, at: list[Any], first: float) -> Any:
    """Return a lance pointing out of the right flank: at the player, once it is broadside."""
    weapon = hidden_weapon(part_id, "lance", at, 7, 900, 2, "red", first, WEAPON_POD)
    mounts = [merge(m, {"restDeg": CASEMATE["restDeg"]}) for m in weapon.mounts]
    return merge(weapon, {"mounts": mounts})


# Its transformations: once both lift engines are gone its armour belts swing out like wings, a
# battery riding each; once both main turrets are gone it turns broadside and its after deck's
# plating bursts off on a rack either side and a lance on the centre line. The hatch over its
# stern rotor bursts as the rotor comes into use, in its last stage (BOSS-58).
CLOUD_DREADNOUGHT = with_weapons(
    merge(
        _CLOUD_DREADNOUGHT,
        {
            "transformParts": [["engine-left", "engine-right"], ["turret-fore", "turret-aft"]],
            "turns": TURNS,
        },
    ),
    [
        _battery("battery-left", [-BATTERY_AT[0], BATTERY_AT[1]], 1.2),
        _battery("battery-right", BATTERY_AT, 2.0),
        hidden_weapon(
            "rack-left",
            "rack",
            [-RACK_AT[0], RACK_AT[1]],
            7,
            900,
            2,
            "orange",
            1.2,
            WEAPON_POD,
        ),
        hidden_weapon("rack-right", "rack", RACK_AT, 7, 900, 2, "orange", 2.0, WEAPON_POD),
        _lance("lance", LANCE_AT, 1.6),
    ],
    concat(
        moving_region("belt", 1, BELT, BELT_SWING, None, BELT_HEIGHTS),
        [
            armour_region(
                "plating",
                2,
                [
                    [PLATING[0], PLATING[2]],
                    [PLATING[1], PLATING[2]],
                    [PLATING[1], PLATING[3]],
                    [PLATING[0], PLATING[3]],
                ],
                "shell",
                [DECK, PLATING_TOP],
                False,
            ),
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 5.5 * math.cos(k * math.pi / 4 + math.pi / 8),
                        ROTOR_AT[1] + 5.5 * math.sin(k * math.pi / 4 + math.pi / 8),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "core-rotor",
            ),
        ],
    ),
)
