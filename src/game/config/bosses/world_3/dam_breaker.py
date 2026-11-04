# Copyright (c) 2026 Renaud Guillon
"""3-4.

The Dam Breaker, the final boss of the swamp works, fought over the giant dam
(specs/bosses/final/3-4-dam-breaker.md).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). The stage
patterns are the agent's design (FB-DAM-BREAKER-09): the parts fire the same while they stand, the
core fires something new at every stage, and its last stage (only the core left) spirals used by no
earlier stage. Health (FB-DAM-BREAKER-07) tuned for WLD-3-20.
"""

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


RED = bullet("red", 205)
MAGENTA = bullet("magenta", 200)
ORANGE = bullet("orange", 195)
GREEN = bullet("green", 190)
# A sluice's sludge: slow, big globs let out in waves the player weaves through
# (FB-DAM-BREAKER-08).
SLUDGE = bullet("green", 125, 7)


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part.

    Drops a bonus 60 % of the time (FB-DAM-BREAKER-13, `part_drop_chance`).
    """
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


# Where the parts sit (the left ones, at -X; the right ones mirror them).
DAM_SLUICE = [-46, -22]
DAM_TANK = [-76, 14]
DAM_PLATE = [0, -32]
DAM_HANGAR = [0, -58]

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The left sluice gate's spout: the sludge pours from the middle of its lip.
DAM_SPOUT = [[-46, -38, 5]]
# The twin guns on the pump house's front (the core's aimed shots, bursts and fans).
DAM_CORE_GUNS = twin(11, -21, 12)
# The top of the pump house's stack (the core's rings and spirals).
DAM_STACK = [[0, 8, 30]]

SLUICE_X = DAM_SLUICE[0]
SLUICE_Y = DAM_SLUICE[1]
TANK_X = DAM_TANK[0]
TANK_Y = DAM_TANK[1]


def waves(source: str, first: float) -> Any:
    """Return a sluice's waves: a row of five globs, then a row of four between them."""
    return [
        volley.fan(source, 4, 5, 15, SLUDGE, first),
        volley.fan(source, 4, 4, 15, SLUDGE, first + 0.55),
    ]


_DAM_BREAKER = record({
    "id": "dam-breaker",
    "stats": stats(
        record({
            "id": "dam-breaker",
            "name": "Dam Breaker",
            "size": 5.5,
            "coreRadius": 22,
            "coreHealth": 5300,
            "points": 15000,
            "groundSpeed": 0.3,
            "coreDrop": 1,
            "parts": [
                fpart("sluice-left", [SLUICE_X, SLUICE_Y], 15, 1650),
                fpart("sluice-right", [-SLUICE_X, SLUICE_Y], 15, 1650),
                fpart("plate", list(DAM_PLATE), 15, 1900),
                fpart("tank-left", [TANK_X, TANK_Y], 15, 1300, {"shields": False}),
                fpart("tank-right", [-TANK_X, TANK_Y], 15, 1300, {"shields": False}),
                fpart("hangar", list(DAM_HANGAR), 14, 900, {"shields": False}),
            ],
        })
    ),
    # Where it stops and how it moves in place (FB-DAM-BREAKER-06).
    "stopFraction": 0.74,
    "sway": {"amplitude": 32, "period": 11},
    "bob": {"amplitude": 5, "period": 5.5},
    "launches": [{"from": "hangar", "kind": "hornets", "count": 2, "every": 7, "first": 3.5}],
    "breakRings": {
        "tank-left": {"count": 12, "bullet": GREEN},
        "tank-right": {"count": 12, "bullet": GREEN},
    },
    "guns": {
        "core": {"gun": DAM_CORE_GUNS, "ring": DAM_STACK},
        "sluice-left": {"gun": DAM_SPOUT},
        "sluice-right": {"gun": mirror(DAM_SPOUT)},
    },
    # The parts' volleys, then the core's pattern per stage (FB-DAM-BREAKER-09).
    "stages": stages(
        concat(waves("sluice-left", 1), waves("sluice-right", 3)),
        [
            [volley.aimed("core", 2.8, 1, 0, RED, 1.4)],
            [volley.aimed("core", 2.4, 3, 12, RED, 0.8)],
            [volley.burst("core", 2.4, 4, 0.13, ORANGE, 0.6)],
            [volley.fan("core", 2.4, 5, 14, MAGENTA, 0.6)],
            [
                volley.fan("core", 2.2, 7, 12, MAGENTA, 0.6),
                volley.burst("core", 2.8, 3, 0.13, RED, 1.2),
            ],
            [
                volley.ring("core", 1.8, 10, 7, GREEN, 0.5),
                volley.aimed("core", 2.6, 1, 0, RED, 1.2),
            ],
            [
                volley.ring("core", 1.3, 14, 9, GREEN, 0.4),
                volley.ring("core", 1.3, 14, -11, ORANGE, 1.05),
            ],
        ],
    ),
})

# Its hidden weapons (boss transformations, D-224): at transformation 1 its flank armour bursts off,
# baring a dark metal frame, and a pair of gun batteries unfold (FB-DAM-BREAKER-11); at
# transformation 2 its wing armour bursts off, baring a dark metal frame, and a pair of missile
# racks unfold (FB-DAM-BREAKER-12).
DAM_BREAKER = with_weapons(
    _DAM_BREAKER,
    [
        hidden_weapon("battery-left", "battery", [-50, 41], 12, 1520, 1, "green", 1.2, 9.4),
        hidden_weapon("battery-right", "battery", [50, 41], 12, 1520, 1, "green", 2.0, 9.4),
        hidden_weapon("rack-left", "rack", [-34, -55], 12, 1900, 2, "green", 1.2, 9.4),
        hidden_weapon("rack-right", "rack", [34, -55], 12, 1900, 2, "green", 2.0, 9.4),
    ],
    [
        # FB-DAM-BREAKER-11: the plating over each flank's deck, from the sluice mounts back to
        # the stern, out to the deck's edge (mirrored); a battery lies under each.
        armour_region(
            "flanks",
            1,
            [[30, 7], [56, 7], [56, 52], [50.5, 65], [35.5, 70], [30, 70]],
            "wing",
        ),
        # FB-DAM-BREAKER-12: the plating over each side of the bow's deck, beside the armour plate
        # and the hangar, out to the deck's edge (mirrored); a rack lies under each.
        armour_region(
            "wings",
            2,
            [[14, -71], [21.5, -70], [39, -62], [52.3, -47], [56, -30], [56, -21], [14, -21]],
            "wing",
        ),
    ],
)
