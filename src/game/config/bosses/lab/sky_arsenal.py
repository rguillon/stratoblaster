# Copyright (c) 2026 Renaud Guillon
"""The Lab's L-14 final boss, the Sky Arsenal (specs/bosses/lab/L-14-sky-arsenal.md).

Lab boss: in the dev viewer only (no level brings it in). A tiered flying fortress stacked like a
wedding cake of gun decks: a broad square lower tier (its four corners are bastion petals), a
smaller middle tier, a small top tier, lift engines slung under the lower tier's flanks and
ammunition cranes on the middle tier. At its first transformation its top tier turns 45 degrees on
its turntable (it changes shape, BOSS-45), its gun stumps going round with it, and the hatches its
corners uncover on the middle tier burst on a pair of mortars. At its second the whole fortress
turns round (BOSS-46) while its four corner petals slide out of the lower tier: a missile rack rides
out on each rear petal, now facing the player, and the stern plating bursts on an orb.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount, laser_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# FB-SKY-ARSENAL-01: the three tiers, each a square: their half widths and their decks' heights.
# The lower tier's corners beyond |x| + |y| = `PETAL_CUT` are its four petals.
LOW_HALF = 50
LOW_TOP = 10
MID_HALF = 36
MID_TOP = 21
TOP_HALF = 24
TOP_TOP = 31
PETAL_CUT = 64
# FB-SKY-ARSENAL-05: the top tier turns this many degrees on its turntable (about the vertical,
# through its centre); the petals slide this far out along their diagonals.
TOP_TURN = 45
PETAL_OUT = 10
TOP_SWING = swing([0, 0, MID_TOP], "up", [0, TOP_TURN])
PETAL_SLIDE_FRONT = slide([[0, 0, 0], [PETAL_OUT, -PETAL_OUT, 0]])
PETAL_SLIDE_BACK = slide([[0, 0, 0], [PETAL_OUT, PETAL_OUT, 0]])
# The heights a petal is drawn between (it stands a little proud of the lower deck).
PETAL_Y = [0, LOW_TOP + 1]


def top_tier() -> list[list[float]]:
    """Return the top tier's outline as drawn, square on at rest."""
    h = TOP_HALF
    return [[-h, -h], [h, -h], [h, h], [-h, h]]


def front_petal() -> list[list[float]]:
    """Return the front right petal's outline as drawn, shut (its left one is its mirror image)."""
    c = PETAL_CUT - LOW_HALF
    return [[c, -LOW_HALF], [LOW_HALF, -LOW_HALF], [LOW_HALF, -c]]


def back_petal() -> list[list[float]]:
    """Return the back right petal's outline as drawn, shut."""
    c = PETAL_CUT - LOW_HALF
    return [[LOW_HALF, c], [LOW_HALF, LOW_HALF], [c, LOW_HALF]]


# The parts (FB-SKY-ARSENAL-03): the top tier's two gun decks, the front petals' bastions, the
# crane on the middle tier's back left corner.
DECK_AT = [12, -11]
BASTION_AT = [39, -39]
CRANE_AT = [-27, 27]
# Where the mortars stand on the middle tier, under the top tier's front corners at rest
# (FB-SKY-ARSENAL-10), the racks on the back petals once slid out, the orb on the stern
# (FB-SKY-ARSENAL-11).
MORTAR_AT = [27, -27]
RACK_AT = [39 + PETAL_OUT, 39 + PETAL_OUT]
ORB_AT = [0, 41]
# The lift engines' ducts out on the lower tier's flanks (FB-SKY-ARSENAL-02): their centres' X and
# their ducts' radius.
ENGINE_X = 62
ENGINE_RADIUS = 12

BLUE = bullet("blue", 185)
ORANGE = bullet("orange", 175)
RED = bullet("red", 190)


def fpart(part_id: str, at: list[Any], radius: float, health: float) -> Any:
    """Return a final boss's part: drops a bonus 60 % of the time (BOSS-57)."""
    return part(part_id, at, radius, health, {"drop": 0.6})


# The guns: a five-barrelled fan turret on each gun deck, three barrels on the bastions' turrets, a
# laser turret on the crane's cab, and the core's: a bow turret on the lower tier's front deck and
# a rotor under a hatch on the top tier (its last ring).
DECK_GUN = {"size": 5.5, "barrels": 5, "gap": 1, "bore": 1, "length": 8}
BASTION_GUN = {"size": 5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 7.5}
CRANE_LASER = {"size": 5, "bore": 2.2, "length": 10, "turret": True}
BOW_GUN = {"size": 5.5, "barrels": 3, "gap": 1.2, "bore": 1.1, "length": 8}
ROTOR = {"size": 5.5, "barrels": 16, "layout": "ring", "bore": 0.7, "length": 3.4}
BOW_AT = [0, -43]
ROTOR_AT = [0, 0]
DECK_GUN_HEIGHT = TOP_TOP + 1.5
BASTION_GUN_HEIGHT = PETAL_Y[1] + 4
CRANE_HEIGHT = MID_TOP + 6

_SKY_ARSENAL = record({
    "id": "sky-arsenal",
    # Its points, its core's drop and its parts' drops (FB-SKY-ARSENAL-13).
    "stats": stats({
        "id": "sky-arsenal",
        "name": "Sky Arsenal",
        "size": 5,
        "coreRadius": 22,
        "coreHealth": 4700,
        "points": 13000,
        "groundSpeed": 0.3,
        "coreDrop": 1,
        "parts": [
            fpart("deck-left", [-DECK_AT[0], DECK_AT[1]], 9, 1300),
            fpart("deck-right", DECK_AT, 9, 1300),
            fpart("bastion-left", [-BASTION_AT[0], BASTION_AT[1]], 10, 1500),
            fpart("bastion-right", BASTION_AT, 10, 1500),
            fpart("crane", CRANE_AT, 10, 1600),
        ],
    }),
    # Where it stops and how it moves in place (FB-SKY-ARSENAL-06): a heavy, slow drift.
    "stopFraction": 0.73,
    "sway": {"amplitude": 28, "period": 11},
    "bob": {"amplitude": 5, "period": 4.5},
    "guns": {},
    # Its gun mounts (BOSS-58, FB-SKY-ARSENAL-03).
    "mounts": [
        gun_mount("deck-left", "deck-left", [-DECK_AT[0], DECK_AT[1]], DECK_GUN_HEIGHT, DECK_GUN),
        gun_mount("deck-right", "deck-right", DECK_AT, DECK_GUN_HEIGHT, DECK_GUN),
        gun_mount(
            "bastion-left",
            "bastion-left",
            [-BASTION_AT[0], BASTION_AT[1]],
            BASTION_GUN_HEIGHT,
            BASTION_GUN,
        ),
        gun_mount("bastion-right", "bastion-right", BASTION_AT, BASTION_GUN_HEIGHT, BASTION_GUN),
        laser_mount("crane", "crane", CRANE_AT, CRANE_HEIGHT, CRANE_LASER),
        gun_mount("bow-gun", "core", BOW_AT, LOW_TOP + 1, BOW_GUN),
        gun_mount("top-rotor", "core", ROTOR_AT, TOP_TOP + 1, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (FB-SKY-ARSENAL-08): stacked, the gun
    # decks' wide fans swept straight down, the bastions' aimed bursts and the crane's aimed laser;
    # the bow turret's aimed shots, spreads, bursts and fans, ending in the top rotor's ring.
    "stages": stages(
        [
            volley.fan("deck-left", 3.0, 5, 10, ORANGE, 1.0),
            volley.fan("deck-right", 3.0, 5, 10, ORANGE, 2.4),
            volley.burst("bastion-left", 2.6, 3, 0.14, RED, 1.4),
            volley.burst("bastion-right", 2.6, 3, 0.14, RED, 2.7),
            volley.laser("crane", 7.5, 1.4, 4.0),
        ],
        [
            [volley.aimed("core", 2.6, 1, 0, BLUE, 1.4)],
            [volley.aimed("core", 2.4, 3, 10, BLUE, 1)],
            [
                volley.burst("core", 1.8, 4, 0.14, BLUE, 0.6),
                volley.aimed("core", 2.4, 3, 8, RED, 1.5),
            ],
            [
                volley.fan("core", 2.2, 5, 12, BLUE, 0.6),
                volley.aimed("core", 2.6, 1, 0, RED, 1.3),
            ],
            [
                volley.fan("core", 2.0, 7, 10, BLUE, 0.6),
                volley.burst("core", 2.6, 3, 0.14, RED, 1.4),
            ],
            [
                volley.ring("core", 1.3, 16, 9, ORANGE, 0.4),
                volley.burst("core", 2.4, 4, 0.14, BLUE, 1),
            ],
        ],
    ),
})

# Its transformations: once both gun decks are gone the top tier turns 45° on its turntable and
# the hatches its front corners uncover burst on a pair of mortars; once both bastions are gone it
# turns round while its four corner petals slide out, a rack riding out on each back petal, and the
# stern plating bursts on an orb on the centre line. The hatch over the top rotor bursts as the
# rotor comes into use, in its last stage (BOSS-58).
SKY_ARSENAL = with_weapons(
    merge(
        _SKY_ARSENAL,
        {
            "transformParts": [["deck-left", "deck-right"], ["bastion-left", "bastion-right"]],
            "turns": [0, math.pi],
        },
    ),
    [
        hidden_weapon(
            "mortar-left",
            "mortar",
            [-MORTAR_AT[0], MORTAR_AT[1]],
            7,
            1280,
            1,
            "orange",
            1.2,
            [MID_TOP, MID_TOP + 3],
        ),
        hidden_weapon(
            "mortar-right", "mortar", MORTAR_AT, 7, 1280, 1, "orange", 2.0, [MID_TOP, MID_TOP + 3]
        ),
        hidden_weapon(
            "rack-left",
            "rack",
            [-RACK_AT[0], RACK_AT[1]],
            8,
            1600,
            2,
            "blue",
            1.2,
            [PETAL_Y[1], PETAL_Y[1] + 3],
        ),
        hidden_weapon(
            "rack-right", "rack", RACK_AT, 8, 1600, 2, "blue", 2.0, [PETAL_Y[1], PETAL_Y[1] + 3]
        ),
        hidden_weapon("orb", "orb", ORB_AT, 8, 1600, 2, "blue", 1.6, [LOW_TOP, LOW_TOP + 3]),
    ],
    concat(
        concat(
            moving_region("top-tier", 1, top_tier(), TOP_SWING, None, [MID_TOP, 1000], False),
            concat(
                moving_region(
                    "petal-front", 2, front_petal(), PETAL_SLIDE_FRONT, None, [PETAL_Y[0], 1000]
                ),
                moving_region(
                    "petal-back", 2, back_petal(), PETAL_SLIDE_BACK, None, [PETAL_Y[0], 1000]
                ),
            ),
        ),
        [
            armour_region(
                "mortar-hatch",
                1,
                [
                    [MORTAR_AT[0] - 7, MORTAR_AT[1] - 7],
                    [MORTAR_AT[0] + 7, MORTAR_AT[1] - 7],
                    [MORTAR_AT[0] + 7, MORTAR_AT[1] + 7],
                    [MORTAR_AT[0] - 7, MORTAR_AT[1] + 7],
                ],
                "shell",
                [MID_TOP, MID_TOP + 1.5],
            ),
            armour_region(
                "stern-hatch",
                2,
                [
                    [-10, ORB_AT[1] - 8],
                    [10, ORB_AT[1] - 8],
                    [10, ORB_AT[1] + 7],
                    [-10, ORB_AT[1] + 7],
                ],
                "shell",
                [LOW_TOP, LOW_TOP + 1.5],
                False,
            ),
            armour_region(
                "rotor-hatch",
                None,
                [
                    [
                        ROTOR_AT[0] + 7 * math.cos(k * math.pi / 4),
                        ROTOR_AT[1] + 7 * math.sin(k * math.pi / 4),
                    ]
                    for k in range(8)
                ],
                "ring",
                None,
                False,
                "top-rotor",
            ),
        ],
    ),
)
