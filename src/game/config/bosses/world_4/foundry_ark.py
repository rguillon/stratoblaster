# Copyright (c) 2026 Renaud Guillon
"""4-4's final boss: the Foundry Ark (specs/bosses/final/4-4-foundry-ark.md).

Fought over the forge belt. Offsets in px from the boss's centre, X right and Y up (its nose points
down, at -Y). Stage patterns as for the World 3 final bosses (FB-FOUNDRY-ARK-13, D-055): its parts
fire the same while they stand, its blast furnace (the core) fires something new at every stage
(slag blobs bursting into rings among them), and spirals and rings of its own, used by no earlier
stage, once it stands alone. Its core always drops a bonus (FB-FOUNDRY-ARK-20). Health
(FB-FOUNDRY-ARK-09) tuned for WLD-4-22.
"""

import math

from game.config.bosses.boss_kit import (
    bullet,
    bursting,
    cells,
    mirror,
    part,
    stages,
    stats,
    twin,
    volley,
)
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def octagon(radius: float) -> list[list[float]]:
    """Return an octagon of `radius` round the centre, its sides facing the axes."""
    return [
        [
            round(math.cos((k + 0.5) * math.pi / 4) * radius, 2),
            round(math.sin((k + 0.5) * math.pi / 4) * radius, 2),
        ]
        for k in range(8)
    ]


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """Return a final boss's part (FB-FOUNDRY-ARK-20).

    It drops a bonus 60 % of the time (`part_drop_chance`).
    """
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


RED = bullet("red", 215)
ORANGE = bullet("orange", 210)
MAGENTA = bullet("magenta", 205)
PURPLE = bullet("purple", 200)
# A glob of slag poured from the furnace: slow and big, it bursts into a ring on its way down.
SLAG = bursting("orange", 115, 7, [1.1, 9, bullet("red", 195)])
# The molten metal a destroyed crucible spills: a ring of bullets (as the Dam Breaker's tanks,
# FB-FOUNDRY-ARK-12).
SPILL = bullet("orange", 185)

# Where its parts stand (FB-FOUNDRY-ARK-09): the rail cannons on the outriggers, the chimney row on
# the foredeck, the missile battery on the bow, the crucibles aft either side of the furnace.
ARK_PARTS = record({
    "rail": [72, -12],
    "chimneys": [0, -50],
    "battery": [0, -82],
    "crucible": [60, 42],
})

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), turrets at rest.

# The right rail cannon's emitter, between the tips of its two rails.
ARK_RAIL = [[ARK_PARTS.rail[0], -52, 8]]
# The missile battery's four cells, 2 columns by 2 rows.
ARK_CELLS = cells([-5.5, 5.5], [-87, -77], 9.1)
# The furnace's twin tap guns, low on its front.
ARK_TAPS = twin(9, -33, 7)
# The furnace's throat, at the top of its stack (the core's rings and spirals).
ARK_THROAT = [0, 0, 36]

RX = ARK_PARTS.rail[0]
RY = ARK_PARTS.rail[1]
CX = ARK_PARTS.crucible[0]
CY = ARK_PARTS.crucible[1]

# 4-4: a huge flying foundry of sooty iron under orange neon, molten seams glowing between its
# plates (FB-FOUNDRY-ARK-01); two rail cannons on turrets aim lasers and, with the chimney row,
# shield the blast furnace at its heart; a missile battery on the bow; two glowing crucibles aft
# that spill into rings of bullets when destroyed. The battery hangs in front of the chimneys and
# the crucibles stand clear of the furnace, so every part can be shot.
_FOUNDRY_ARK = record({
    "id": "foundry-ark",
    # Its core and parts, their health, and its points (FB-FOUNDRY-ARK-09).
    "stats": stats(
        record({
            "id": "foundry-ark",
            "name": "Foundry Ark",
            "size": 6,
            "coreRadius": 28,
            "coreHealth": 5600,
            "points": 20000,
            "groundSpeed": 0.3,
            "coreDrop": 1,
            "parts": [
                fpart("rail-left", [-RX, RY], 19, 1500),
                fpart("rail-right", [RX, RY], 19, 1500),
                fpart("chimneys", list(ARK_PARTS.chimneys), 16, 2400),
                fpart("battery", list(ARK_PARTS.battery), 13, 900, {"shields": False}),
                fpart("crucible-left", [-CX, CY], 15, 1450, {"shields": False}),
                fpart("crucible-right", [CX, CY], 15, 1450, {"shields": False}),
            ],
        })
    ),
    # Where it stops and how it moves in place (FB-FOUNDRY-ARK-08).
    "stopFraction": 0.75,
    "sway": {"amplitude": 28, "period": 12},
    "bob": {"amplitude": 5, "period": 5.5},
    "breakRings": {
        "crucible-left": {"count": 14, "bullet": SPILL},
        "crucible-right": {"count": 14, "bullet": SPILL},
    },
    "guns": {
        "core": {"gun": ARK_TAPS, "ring": [ARK_THROAT]},
        "rail-left": {"laser": mirror(ARK_RAIL), "turret": [-RX, RY], "turretLaser": True},
        "rail-right": {"laser": ARK_RAIL, "turret": [RX, RY], "turretLaser": True},
        "battery": {"missile": ARK_CELLS},
    },
    # In every stage the rails' lasers (FB-FOUNDRY-ARK-10) and the battery's missiles
    # (FB-FOUNDRY-ARK-11); then the core's pattern per stage (FB-FOUNDRY-ARK-13).
    "stages": stages(
        [
            volley.laser("rail-left", 6.5, 1.6, 2),
            volley.laser("rail-right", 6.5, 1.6, 5.2),
            volley.missiles("battery", 5.5, 2, 26, 3.5),
        ],
        [
            [volley.burst("core", 2.4, 4, 0.12, RED, 1.4)],
            [volley.fan("core", 2.3, 5, 13, ORANGE, 0.8)],
            [
                volley.aimed("core", 3, 1, 0, SLAG, 0.8),
                volley.aimed("core", 2.2, 3, 10, MAGENTA, 1.9),
            ],
            [
                volley.ring("core", 1.9, 12, 7, ORANGE, 0.6),
                volley.burst("core", 2.6, 3, 0.12, RED, 1.2),
            ],
            [
                volley.fan("core", 2.4, 7, 11, MAGENTA, 0.6),
                volley.ring("core", 0.55, 4, 19, RED, 0.4),
            ],
            [
                volley.ring("core", 0.5, 5, 17, ORANGE, 0.4),
                volley.ring("core", 0.5, 5, -19, PURPLE, 0.65),
            ],
            [
                volley.ring("core", 1.1, 16, 9, ORANGE, 0.4),
                volley.ring("core", 1.1, 16, -11, RED, 0.95),
                volley.fan("core", 3.2, 3, 30, SLAG, 1.4),
                volley.burst("core", 2.6, 4, 0.11, MAGENTA, 1.8),
            ],
        ],
    ),
})

# Its hidden weapons (boss transformations, D-224): at transformation 1 its flank armour bursts off
# (FB-FOUNDRY-ARK-16), baring a dark metal frame, and a pair of gun batteries unfold
# (FB-FOUNDRY-ARK-17); at transformation 2 its wing armour and its spine plating bursts off
# (FB-FOUNDRY-ARK-18), baring a dark metal frame, and a pair of gatling turrets and a drone hangar
# unfold (FB-FOUNDRY-ARK-19).
FOUNDRY_ARK = with_weapons(
    _FOUNDRY_ARK,
    [
        hidden_weapon("battery-left", "battery", [-41, -43], 13, 1920, 1, "orange", 1.2, 10.2),
        hidden_weapon("battery-right", "battery", [41, -43], 13, 1920, 1, "orange", 2.0, 10.2),
        hidden_weapon("gatling-left", "gatling", [-48, 13], 10, 2400, 2, "orange", 1.2, 8.8),
        hidden_weapon("gatling-right", "gatling", [48, 13], 10, 2400, 2, "orange", 2.0, 8.8),
        hidden_weapon("hangar-centre", "hangar", [0, -19], 10, 2400, 2, "orange", 1.6, 22.4),
    ],
    [
        # D-254: iron plates lying on the deck, out to its edge (the fore flank plates from x 20,
        # the aft wing plates from x 30), and the furnace's crown plate (an octagon the hearth's
        # top, its sides facing the axes) carrying the stack.
        armour_region(
            "flanks",
            1,
            [[20, -78], [44.9, -78], [56, -60], [60, -20], [60.3, -13.5], [20, -13.5]],
            "wing",
        ),
        armour_region(
            "wings", 2, [[30, -13.5], [60.3, -13.5], [62, 40], [61.2, 45], [30, 45]], "wing"
        ),
        armour_region("spine", 2, octagon(21), "shell", None, False),
    ],
)
