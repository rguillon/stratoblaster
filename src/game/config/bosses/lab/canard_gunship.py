# Copyright (c) 2026 Renaud Guillon
"""The Canard Gunship, the Lab's L-19 mini boss (specs/bosses/lab/L-19-canard-gunship.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic canard-wing gunship seen from
above: a long boxy fuselage, small canards at its nose, its main wings at the back with winglets on
their tips and an engine on each, a pusher propeller behind it. It comes nose-on, firing aimed
pairs from its canard pods and bursts from its nose gun. Once both canard pods are gone it banks
round into a broadside (BOSS-46, a quarter turn) while its right flank opens up: two cargo doors
fold down outward into firing platforms (moving pieces, BOSS-45), struts telescoping under them,
ammunition racks swing out of the bay onto them and a gatling unfolds on each, railings rising
along their edges (its view rig): a gun gallery raking the screen.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# MB-CANARD-GUNSHIP-01: the fuselage, from its nose to its tail, its half width, its belly, its
# cargo floor (the doors' hinges) and its roof; its nose tapers over `NOSE_TAPER` px.
NOSE = -74
TAIL = 54
HALF = 9
BELLY = 2
FLOOR = 6
ROOF = 20
NOSE_TAPER = 20
# The canards (MB-CANARD-GUNSHIP-02): the right one's root chord `[y0, y1]`, its tip's X and chord,
# and its plate's heights.
CANARD_ROOT = [-60, -46]
CANARD_TIP_X = 31
CANARD_TIP = [-55, -48]
CANARD_H = [11, 12.6]
# The main wings: the right one's root chord, tip X and chord (swept back), their plate's heights;
# a winglet stands on each tip, `WINGLET_TOP` px high.
WING_ROOT = [12, 38]
WING_TIP_X = 62
WING_TIP = [30, 42]
WING_H = [12, 14.4]
WINGLET_TOP = 30
# The engines on the wings: their X, `[y0, y1]`, radius and axis height; the pusher propellers
# behind them: their hub's Y and their blades' reach.
ENGINE_X = 33
ENGINE_Y = [16, 44]
ENGINE_RADIUS = 5
ENGINE_H = 14
PROP_Y = 47
PROP_RADIUS = 11
# The cargo doors down its right flank (MB-CANARD-GUNSHIP-10): `[y0, y1]` of each, hinged at the
# cargo floor on the flank; open, each is a platform `DOOR_REACH` px out, `DOOR_THICK` thick.
DOORS = [[-38, -18], [-14, 6]]  # type: list[list[float]]
DOOR_REACH = 15
DOOR_THICK = 1.2
# Each door turns about its hinge (along the fuselage) from standing closed up the flank (-90°)
# to lying open (0°, as drawn).
DOOR_SWING = swing([HALF, 0, FLOOR], "along", [-90, 0])

RED = bullet("red", 190)
ORANGE = bullet("orange", 180)
GREEN = bullet("green", 175)

# Its guns (BOSS-58, MB-CANARD-GUNSHIP-03): twin barrels on each canard pod's turret, three on the
# nose gun's, and the core's: a twin dorsal turret on the roof and a rotor between the wings (its
# last rings), under a hatch until then.
CANARD_GUN_AT = [25, -51]
CANARD_GUN_H = 16
CANARD_GUN = {"size": 4, "barrels": 2, "gap": 2.8, "bore": 1, "length": 7}
NOSE_GUN_AT = [0, -64]
NOSE_GUN_H = 16.5
NOSE_GUN = {"size": 4.6, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 8}
DORSAL_AT = [0, -6]
DORSAL_GUN = {"size": 4.8, "barrels": 2, "gap": 3, "bore": 1.1, "length": 7.5}
ROTOR_AT = [0, 26]
ROTOR = {"size": 4.4, "barrels": 10, "layout": "ring", "bore": 0.8, "length": 3.4}
GUN_H = ROOF + 0.5

_CANARD_GUNSHIP = record({
    "id": "canard-gunship",
    # Its points and its parts' drops (MB-CANARD-GUNSHIP-12).
    "stats": stats({
        "id": "canard-gunship",
        "name": "Canard Gunship",
        "size": 3.8,
        "coreRadius": 14,
        "coreHealth": 1400,
        "points": 4600,
        "groundSpeed": 1.1,
        "parts": [
            part("canard-left", [-CANARD_GUN_AT[0], CANARD_GUN_AT[1]], 8, 700),
            part("canard-right", CANARD_GUN_AT, 8, 700),
            part("nose-gun", NOSE_GUN_AT, 9, 760),
        ],
    }),
    # Where it stops and how it moves in place (MB-CANARD-GUNSHIP-06): a heavy gunship, slow wide
    # orbits.
    "stopFraction": 0.72,
    "sway": {"amplitude": 55, "period": 8},
    "bob": {"amplitude": 6, "period": 3.4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-CANARD-GUNSHIP-03).
    "mounts": [
        gun_mount(
            "canard-left",
            "canard-left",
            [-CANARD_GUN_AT[0], CANARD_GUN_AT[1]],
            CANARD_GUN_H,
            CANARD_GUN,
        ),
        gun_mount("canard-right", "canard-right", CANARD_GUN_AT, CANARD_GUN_H, CANARD_GUN),
        gun_mount("nose-gun", "nose-gun", NOSE_GUN_AT, NOSE_GUN_H, NOSE_GUN),
        gun_mount("dorsal", "core", DORSAL_AT, GUN_H, DORSAL_GUN),
        gun_mount("spine-rotor", "core", ROTOR_AT, GUN_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-CANARD-GUNSHIP-08): nose-on aimed
    # fire (the canard pods' aimed pairs, the nose gun's bursts, the dorsal turret's aimed shots,
    # spreads and bursts), then the spine rotor's rings of 10.
    "stages": stages(
        [
            volley.aimed("canard-left", 2.2, 2, 6, RED, 0.8),
            volley.aimed("canard-right", 2.2, 2, 6, RED, 1.9),
            volley.burst("nose-gun", 2.6, 3, 0.12, ORANGE, 1.3),
        ],
        [
            [volley.aimed("core", 2.8, 1, 0, GREEN, 1.5)],
            [volley.aimed("core", 2.4, 3, 8, GREEN, 1)],
            [volley.burst("core", 2.2, 4, 0.12, ORANGE, 0.8)],
            [
                volley.ring("core", 1.5, 10, 9, GREEN, 0.4),
                volley.aimed("core", 2.6, 2, 6, RED, 1.2),
            ],
        ],
    ),
})

# Where the gatlings stand (MB-CANARD-GUNSHIP-10): on the open doors, their pods on the platforms.
GATLING_X = HALF + 7.5
GATLING_POD = [FLOOR, FLOOR + 3.5]
# Each gatling unfolds about a hinge on its inner side, by the flank, from lying along it.
GATLING_HINGE = [-6.5, 0, math.pi / 2]
# Their rakes (MB-CANARD-GUNSHIP-08): fans of 9, 9° apart, out of its right flank (90° off its
# nose): once broadside, straight down the screen, each turret sweeping across them.
RAKE_HEADING = 90


def door_outline(k: int) -> list[list[float]]:
    """Return door `k`'s outline as drawn: open, a platform out from the flank."""
    y = DOORS[k]
    return [[HALF, y[0]], [HALF + DOOR_REACH, y[0]], [HALF + DOOR_REACH, y[1]], [HALF, y[1]]]


def _gatling(part_id: str, k: int, first: float) -> Any:
    """Return the gatling on door `k`."""
    y = DOORS[k]
    return hidden_weapon(
        part_id,
        "gatling",
        [GATLING_X, (y[0] + y[1]) / 2 - 1.5],
        7,
        640,
        1,
        "red",
        first,
        GATLING_POD,
        GATLING_HINGE,
    )


def _rake(part_id: str, first: float) -> Any:
    return volley.fan(part_id, 3.4, 9, 9, ORANGE, first, RAKE_HEADING)


# Its transformation (BOSS-45, BOSS-46, MB-CANARD-GUNSHIP-10): once both canard pods are gone it
# banks round into a broadside (a quarter turn clockwise: its nose to the screen's left, its right
# flank to the player), its two cargo doors fold down into platforms and a gatling unfolds on
# each. The hatch over its spine rotor bursts as the rotor comes into use, in its last stage
# (BOSS-58).
CANARD_GUNSHIP = with_weapons(
    merge(
        _CANARD_GUNSHIP,
        {"transformParts": [["canard-left", "canard-right"]], "turns": [math.pi / 2]},
    ),
    [_gatling("gatling-fore", 0, 1.0), _gatling("gatling-aft", 1, 1.8)],
    concat(
        concat(
            moving_region(
                "door-fore", 1, door_outline(0), DOOR_SWING, None, [FLOOR - 1.5, 1000], False
            ),
            moving_region(
                "door-aft", 1, door_outline(1), DOOR_SWING, None, [FLOOR - 1.5, 1000], False
            ),
        ),
        [
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 5.6 * math.cos(k * math.pi / 4 + math.pi / 8),
                        ROTOR_AT[1] + 5.6 * math.sin(k * math.pi / 4 + math.pi / 8),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "spine-rotor",
            ),
        ],
    ),
    [_rake("gatling-fore", 2.2), _rake("gatling-aft", 3.9)],
)
