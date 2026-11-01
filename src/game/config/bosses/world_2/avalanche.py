"""The Avalanche (2-4's mini boss, specs/bosses/mini/2-4-avalanche.md)

The Glacier level's mini boss. Offsets in px from the boss's centre, X right and Y up (its nose
points down, at -Y). Its two drill arms swing on their joints (D-061) and shield the core; a rock
hopper on its back drops lines of slow big rocks (MB-AVALANCHE-10).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

ORANGE = bullet("orange", 180)
RED = bullet("red", 190)
# The hopper's rocks: slow and big, dropped in lines the player weaves through.
ROCK = bullet("purple", 110, 7)

# Where each drill arm's left (-X) joints and drill sit, as drawn at rest (mirrored on the right).
AVALANCHE_ARM = record(
    {
        "shoulder": [-20, -12],
        "elbow": [-34, -24],
        "drill": [-42, -36],
    }
)

# The guns' muzzles (MB-AVALANCHE-03): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The left drill's gun, along the drill's outer side (mirrored on the right).
AVALANCHE_DRILL_GUN = [[-51, -50, 8]]
# The core's twin guns under the cab's chin.
AVALANCHE_CORE_GUNS = twin(6, -40, 5)
# The hopper's chute, at the front of its bin: the rocks fall from its lip.
AVALANCHE_CHUTE = [[0, 15, 12]]


def drill_arm(side: str) -> Any:
    """A drill arm's joints (D-061, MB-AVALANCHE-06), the left one at -X: it swings at the shoulder
    and bends at the elbow, the drill hanging on the elbow. The right arm is its mirror image, a
    little out of step.
    """
    s = 1 if side == "left" else -1
    late = 0 if side == "left" else 0.37

    def joint(position: list[Any], swing: list[Any], parent: str | None = None) -> Any:
        result = record(
            {
                "x": s * position[0],
                "y": position[1],
                "swing": {
                    "amplitudeDeg": s * swing[0],
                    "period": swing[1],
                    "phase": swing[2] + late,
                },
            }
        )
        if parent is not None:
            result["parent"] = parent + "-" + side
        return result

    table: Any = {}
    table["shoulder-" + side] = joint(AVALANCHE_ARM.shoulder, [7, 4.2, 0])
    table["elbow-" + side] = joint(AVALANCHE_ARM.elbow, [12, 2.8, 0.25], "shoulder")
    return table


DRILL_X = AVALANCHE_ARM.drill[0]
DRILL_Y = AVALANCHE_ARM.drill[1]

# 2-4: a heavy drilling machine with two drill arms swinging in front of it (they fire aimed
# bursts and shield the core, MB-AVALANCHE-09) and a rock hopper on its back; the fight is a chase
# down the glacier (ground ×1.4).
_AVALANCHE = record(
    {
        "id": "avalanche",
        # Angry after each destroyed part (phase 7 review, D-063, MB-AVALANCHE-12).
        "rage": rage.spirals(5.5, "orange", "red"),
        # Its core, drills, hopper and points (MB-AVALANCHE-14).
        "stats": stats(
            {
                "id": "avalanche",
                "name": "Avalanche",
                "size": 3.5,
                "coreRadius": 18,
                "coreHealth": 1400,
                "points": 7000,
                "groundSpeed": 1.4,
                "parts": [
                    part("drill-left", [DRILL_X, DRILL_Y], 14, 900, {"joint": "elbow-left"}),
                    part("drill-right", [-DRILL_X, DRILL_Y], 14, 900, {"joint": "elbow-right"}),
                    part("hopper", [0, 31], 14, 600, {"shields": False}),
                ],
                "joints": merge(drill_arm("left"), drill_arm("right")),
            }
        ),
        # Where it stops and how it moves in place; its ground speed is a chase (MB-AVALANCHE-08).
        "stopFraction": 0.74,
        "sway": {"amplitude": 60, "period": 7.5},
        "bob": {"amplitude": 8, "period": 3.2},
        "guns": {
            "core": {"gun": AVALANCHE_CORE_GUNS},
            "drill-left": {"gun": AVALANCHE_DRILL_GUN},
            "drill-right": {"gun": mirror(AVALANCHE_DRILL_GUN)},
            "hopper": {"gun": AVALANCHE_CHUTE},
        },
        # The drills' bursts and the hopper's rocks, then the core's pattern per stage
        # (MB-AVALANCHE-11).
        "stages": stages(
            [
                volley.burst("drill-left", 2.4, 3, 0.16, RED, 1),
                volley.burst("drill-right", 2.4, 3, 0.16, RED, 2.2),
                # Rows of rocks straight down, every other row offset: a lattice to weave through.
                volley.fan("hopper", 4, 3, 26, ROCK, 1.5),
                volley.fan("hopper", 4, 2, 26, ROCK, 2),
                volley.fan("hopper", 4, 3, 26, ROCK, 2.5),
            ],
            [
                [volley.fan("core", 3.2, 3, 16, ORANGE, 1.8)],
                [volley.fan("core", 2.6, 5, 14, ORANGE, 0.8)],
                [volley.fan("core", 2.2, 7, 12, ORANGE, 0.6)],
                [
                    volley.ring("core", 1.6, 12, 9, ORANGE, 0.4),
                    volley.fan("core", 2.6, 5, 14, RED, 1),
                ],
            ],
        ),
    }
)

# Its hidden weapons (boss transformations, D-224, MB-AVALANCHE-13): at transformation 1 its flank
# armour bursts off, baring a dark metal frame (MB-AVALANCHE-07), and a pair of heavy cannons
# unfold.
AVALANCHE = with_weapons(
    _AVALANCHE,
    [
        hidden_weapon("cannon-left", "cannon", [-29, 21], 11, 720, 1, "purple", 1.2, 12.2),
        hidden_weapon("cannon-right", "cannon", [29, 21], 11, 720, 1, "purple", 2.0, 12.2),
    ],
    [
        armour_region("flanks", 1, [[10, -12], [44, -12], [44, 38], [10, 38]], "wing", [4.2, 1000]),
    ],
)
