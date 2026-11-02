# Copyright (c) 2026 Renaud Guillon
"""3-2.

The Canopy Spider, the final boss of the Rainforest level (specs/bosses/final/3-2-canopy-spider.md).

Offsets in px from the boss's centre, X right and Y up, its head points down, at -Y. Its four legs
bend at the hip and the knee (D-061), stepping in turn, each out of step with the others. Stage
patterns as for the World 1 and 2 bosses (FB-CANOPY-SPIDER-10): the legs fire the same while they
stand, the core spirals in a new way at every stage, and its last stage (only the core left) is a
double spiral used by no earlier stage. Health (FB-CANOPY-SPIDER-08) tuned with the D-055 bot for
WLD-3-20.
"""

from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


RED = bullet("red", 205)
PURPLE = bullet("purple", 195)
MAGENTA = bullet("magenta", 200)
GREEN = bullet("green", 190)


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part.

    Drops a bonus 60 % of the time (FB-CANOPY-SPIDER-14, `part_drop_chance`).
    """
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


# The legs in the order of their parts (`fore` towards the head, `aft` towards the abdomen).
LEGS = ["fore-left", "fore-right", "aft-left", "aft-right"]

# Where a left leg (at -X) bends and holds its gun, as drawn at rest: its hip (on the body), its
# knee and its foot (the gun pod's centre). The right legs mirror them.
LEG_REST = record({
    "fore": [[-11, -20], [-24, -40], [-28, -62]],
    "aft": [[-16, 6], [-48, 18], [-70, 36]],
})

# Heights of a leg (model units over the playfield): its hip, its raised knee, its foot.
LEG_HEIGHT = record({"hip": 8, "knee": 22, "foot": 4})

# The stepping cycle: degrees at the hip and the knee, and the seconds of one step.
STEP = record({"hipDeg": 11, "kneeDeg": 15, "period": 3.2})

# Each leg's phase in the stepping cycle (phase 7 review, D-061, FB-CANOPY-SPIDER-03): a walking
# order (fore-left, aft-right, fore-right, aft-left), so that the four legs step in turn and never
# together.
PHASE = record({"fore-left": 0, "aft-right": 0.25, "fore-right": 0.5, "aft-left": 0.75})


def side_of(leg: str) -> Any:
    """Return the side of `leg`: +1 for a left one, -1 for a right one.

    A left leg is drawn at -X, as in `LEG_REST`.
    """
    return 1 if leg.endswith("left") else -1


def end_of(leg: str) -> Any:
    """Return the end of the body `leg` is on."""
    return "fore" if leg.startswith("fore") else "aft"


def leg_joints(leg: str) -> Any:
    """Return the hip and knee joints of `leg`.

    The knee lags a quarter step behind the hip, so the foot swings forward with the knee bent and
    comes back with it straight (a step, seen from above).
    """
    s = side_of(leg)
    end = end_of(leg)
    hip = LEG_REST[end][0]
    knee = LEG_REST[end][1]
    phase = PHASE[leg]
    joints: dict[str, Any] = {}
    joints["hip-" + leg] = {
        "x": s * hip[0],
        "y": hip[1],
        "swing": {"amplitudeDeg": s * STEP.hipDeg, "period": STEP.period, "phase": phase},
    }
    joints["knee-" + leg] = {
        "x": s * knee[0],
        "y": knee[1],
        "parent": "hip-" + leg,
        "swing": {
            "amplitudeDeg": -s * STEP.kneeDeg,
            "period": STEP.period,
            "phase": phase + 0.25,
        },
    }
    return joints


def all_leg_joints() -> Any:
    """Return the joints of all four legs, merged (`Object.assign({}, ...LEGS.map(legJoints))`)."""
    joints: Any = {}
    for leg in LEGS:
        joints = merge(joints, leg_joints(leg))
    return joints


# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.

# How far ahead of its foot a leg gun's barrel ends (screen px, towards -Y).
LEG_GUN_REACH = 11.6


def leg_gun(end: str) -> Any:
    """Return the leg guns' barrels: the left fore one's and the left aft one's.

    The right ones are mirrored.
    """
    pos = LEG_REST[end][2]
    return [pos[0], pos[1] - LEG_GUN_REACH, LEG_HEIGHT.foot]


# The crown emitter on its back: the core's spirals leave from there.
SPIDER_CROWN = [[0, -2, 21]]


def leg_gun_pod(leg: str, health: float) -> Any:
    """Return a leg's gun pod, on its knee (the part's centre is its foot)."""
    pos = LEG_REST[end_of(leg)][2]
    return fpart(
        "leg-" + leg, [side_of(leg) * pos[0], pos[1]], 12, health, {"joint": "knee-" + leg}
    )


def leg_muzzles(leg: str) -> Any:
    """Return the muzzle of `leg`'s gun."""
    g = leg_gun(end_of(leg))
    return [[side_of(leg) * g[0], g[1], g[2]]]


def leg_guns() -> Any:
    """Return the gun of each leg's part, keyed by part id."""
    guns: dict[str, Any] = {}
    for leg in LEGS:
        guns["leg-" + leg] = {"gun": leg_muzzles(leg)}
    return guns


_CANOPY_SPIDER = record({
    "id": "canopy-spider",
    # Angry after each destroyed part (phase 7 review, FB-CANOPY-SPIDER-11).
    "rage": rage.flower(6, "red", "purple"),
    # Its core, leg gun pods and egg sac (FB-CANOPY-SPIDER-08).
    "stats": stats(
        record({
            "id": "canopy-spider",
            "name": "Canopy Spider",
            "size": 5,
            "coreRadius": 22,
            "coreHealth": 3150,
            "points": 14000,
            "groundSpeed": 0.4,
            "coreDrop": 1,
            "parts": concat(
                [leg_gun_pod(leg, 1250) for leg in LEGS],
                [fpart("egg-sac", [0, 50], 15, 900, {"shields": False})],
            ),
            "joints": all_leg_joints(),
        })
    ),
    # Where it stops and how it moves in place (FB-CANOPY-SPIDER-07).
    "stopFraction": 0.74,
    "sway": {"amplitude": 30, "period": 11},
    "bob": {"amplitude": 6, "period": 5},
    # The egg sac launches Gnats, the legs fire aimed shots (FB-CANOPY-SPIDER-09).
    "launches": [{"from": "egg-sac", "kind": "gnats", "count": 3, "every": 7, "first": 3}],
    "guns": merge({"core": {"ring": SPIDER_CROWN}}, leg_guns()),
    # The legs' volleys, then the core's pattern per stage (FB-CANOPY-SPIDER-10).
    "stages": stages(
        [volley.aimed("leg-" + leg, 3.4, 3, 12, RED, 1 + 0.85 * i) for i, leg in enumerate(LEGS)],
        [
            [volley.ring("core", 1.5, 8, 13, PURPLE, 0.6)],
            [volley.ring("core", 1.4, 9, -15, MAGENTA, 0.5)],
            [volley.ring("core", 1.3, 10, 17, PURPLE, 0.5)],
            [
                volley.ring("core", 1.5, 8, 12, PURPLE, 0.4),
                volley.ring("core", 1.5, 8, -12, MAGENTA, 1.15),
            ],
            [
                volley.ring("core", 1.2, 11, 19, MAGENTA, 0.4),
                volley.ring("core", 2.4, 7, -9, PURPLE, 1),
            ],
            [
                volley.ring("core", 1.1, 12, 9, GREEN, 0.3),
                volley.ring("core", 1.1, 12, -13, GREEN, 0.85),
            ],
        ],
    ),
})

# Its hidden weapons (boss transformations, D-224): at transformation 1 its back plating bursts off,
# baring a dark metal frame, and a pair of gatling turrets unfold (FB-CANOPY-SPIDER-12); at
# transformation 2 its spine plating bursts off, baring a dark metal frame, and a pair of laser
# lances unfold (FB-CANOPY-SPIDER-13).
CANOPY_SPIDER = with_weapons(
    _CANOPY_SPIDER,
    [
        hidden_weapon("gatling-left", "gatling", [-13, 25], 7, 1000, 1, "red", 1.2, 22.3),
        hidden_weapon("gatling-right", "gatling", [13, 25], 7, 1000, 1, "red", 2.0, 22.3),
        hidden_weapon("lance-left", "lance", [-9, -21], 7, 1250, 2, "red", 1.2, 12.8),
        hidden_weapon("lance-right", "lance", [9, -21], 7, 1250, 2, "red", 2.0, 12.8),
    ],
    [
        armour_region(
            "back", 1, [[-28, 2], [28, 2], [28, 49], [-28, 49]], "shell", [7.0, 1000], False
        ),
        armour_region(
            "spine", 2, [[-24, -42], [24, -42], [24, 2], [-24, 2]], "shell", [6.4, 1000], False
        ),
    ],
)
