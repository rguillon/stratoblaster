# Copyright (c) 2026 Renaud Guillon
"""The Ice Queen (2-5's mini boss, specs/bosses/mini/2-5-ice-queen.md).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Stage
patterns as for the World 1 mini bosses (`mini_bosses.py`, MB-ICE-QUEEN-10): the shards fire
spirals while they stand, the core fires aimed bursts that change at every stage, and a spiral of
its own, used by no earlier stage, once it stands alone.
"""

import math

from game.config.bosses.boss_kit import bullet, part, stages, stats, twin, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


PURPLE = bullet("purple", 190)
MAGENTA = bullet("magenta", 195)
BLUE = bullet("blue", 185)

# The crown ring's crystal shards (MB-ICE-QUEEN-03): their centres turn `orbit` px from the core,
# `height` above the playfield; each shard lies along the ring, a muzzle at both its tips, `reach`
# px from its centre (it fires both ways along the ring). The model draws them from these numbers.
ICE_QUEEN_SHARD = record({"orbit": 42, "reach": 13, "height": 13})

# The shards' turns around the core at a spin of 0, from the nose (radians, clockwise on screen).
SHARD_TURNS = [0, (2 * math.pi) / 3, (4 * math.pi) / 3]


def shard_at(turn: float) -> list[Any]:
    """Where a shard turned by `turn` stands on the playfield at a spin of 0."""
    return [
        ICE_QUEEN_SHARD.orbit * math.sin(turn),
        -ICE_QUEEN_SHARD.orbit * math.cos(turn),
    ]


def shard_muzzles(turn: float) -> list[list[Any]]:
    """Return the two tips of the shard turned by `turn`, along the ring.

    They are where its bullets leave from.
    """
    position = shard_at(turn)
    x = position[0]
    y = position[1]
    reach = ICE_QUEEN_SHARD.reach
    height = ICE_QUEEN_SHARD.height
    return [
        [
            x + s * reach * math.cos(turn),
            y + s * reach * math.sin(turn),
            height,
        ]
        for s in [-1, 1]
    ]


# The twin crystal cannons on either side of the nose (aimed bursts).
ICE_QUEEN_NOSE_GUNS = twin(6.5, -52, 3.2)
# The tip of the crystal spire over the core, under the crown (its last spiral).
ICE_QUEEN_SPIRE = [0, 0, 25]


def ice_queen_parts() -> list[object]:
    """Return the three shards, on the ring at the turns of `SHARD_TURNS`."""
    return [
        part("shard-" + str(i + 1), shard_at(turn), 13, 840, {"orbits": True})
        for i, turn in enumerate(SHARD_TURNS)
    ]


# 2-5: a slender crystal interceptor under a turning crown ring; three crystal shards on the ring
# fire spirals and shield the core (MB-ICE-QUEEN-09), which fires aimed bursts from its nose.
_ICE_QUEEN = record({
    "id": "ice-queen",
    # Its core, shards and points (MB-ICE-QUEEN-13).
    "stats": stats({
        "id": "ice-queen",
        "name": "Ice Queen",
        "size": 3.5,
        "coreRadius": 18,
        "coreHealth": 1680,
        "points": 7000,
        "groundSpeed": 0.6,
        "parts": ice_queen_parts(),
    }),
    # Where it stops and how it moves in place (MB-ICE-QUEEN-08).
    "stopFraction": 0.74,
    "sway": {"amplitude": 65, "period": 6.5},
    "bob": {"amplitude": 8, "period": 3},
    # The crown ring turns, carrying the shards round the core (MB-ICE-QUEEN-06).
    "spinRate": 0.85,
    "guns": {
        "core": {"gun": ICE_QUEEN_NOSE_GUNS, "ring": [ICE_QUEEN_SPIRE]},
        "shard-1": {"gun": shard_muzzles(SHARD_TURNS[0])},
        "shard-2": {"gun": shard_muzzles(SHARD_TURNS[1])},
        "shard-3": {"gun": shard_muzzles(SHARD_TURNS[2])},
    },
    # The shards' spirals, then the core's pattern per stage (MB-ICE-QUEEN-10).
    "stages": stages(
        [
            volley.ring("shard-1", 0.9, 2, 21, PURPLE, 0.4),
            volley.ring("shard-2", 0.9, 2, 21, PURPLE, 0.7),
            volley.ring("shard-3", 0.9, 2, 21, PURPLE, 1),
        ],
        [
            [volley.burst("core", 2.6, 3, 0.15, MAGENTA, 1.4)],
            [volley.burst("core", 2.3, 4, 0.13, MAGENTA, 0.8)],
            [
                volley.burst("core", 2.2, 5, 0.11, MAGENTA, 0.6),
                volley.aimed("core", 3.3, 3, 14, BLUE, 1.7),
            ],
            [
                volley.ring("core", 1.2, 14, 11, BLUE, 0.4),
                volley.burst("core", 2.4, 4, 0.12, MAGENTA, 1),
            ],
        ],
    ),
})

# Its hidden weapons (boss transformations, D-224, MB-ICE-QUEEN-12): at transformation 1 its back
# plating bursts off, baring a dark metal frame (MB-ICE-QUEEN-07), and a pair of gun batteries
# unfold.
ICE_QUEEN = with_weapons(
    _ICE_QUEEN,
    [
        hidden_weapon("battery-left", "battery", [-12, 39], 10, 670, 1, "purple", 1.2, 16.5),
        hidden_weapon("battery-right", "battery", [12, 39], 10, 670, 1, "purple", 2.0, 16.5),
    ],
    [
        # MB-ICE-QUEEN-07: the plating over its rear (its nose at -Y): a lozenge over the rear
        # deck and the engine sacs, from the spire's gland to the tail; the batteries lie under it.
        armour_region(
            "back",
            1,
            [
                [-2, 6],
                [2, 6],
                [13, 14],
                [16, 26],
                [16, 44],
                [12, 50],
                [3, 57],
                [-3, 57],
                [-12, 50],
                [-16, 44],
                [-16, 26],
                [-13, 14],
            ],
            "shell",
            None,
            False,
        ),
    ],
)
