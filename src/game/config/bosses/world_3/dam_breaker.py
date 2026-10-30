"""P09-R09, 3-4: the Dam Breaker, the final boss of the swamp works, fought over the giant dam
(ported from `config/bosses/world-3/dam-breaker.ts`).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). The stage
patterns are the agent's design (P07-R04): the parts fire the same while they stand, the core fires
something new at every stage, and its last stage (only the core left) spirals used by no earlier
stage. Health tuned for P09-R10.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

RED = bullet("red", 205)
MAGENTA = bullet("magenta", 200)
ORANGE = bullet("orange", 195)
GREEN = bullet("green", 190)
# A sluice's sludge: slow, big globs let out in waves the player weaves through (P09-R09).
SLUDGE = bullet("green", 125, 7)


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
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
    """A sluice's waves: a row of five globs, then a row of four between them."""
    return [
        volley.fan(source, 4, 5, 15, SLUDGE, first),
        volley.fan(source, 4, 4, 15, SLUDGE, first + 0.55),
    ]


DAM_BREAKER = record(
    {
        "id": "dam-breaker",
        # Angry after each destroyed part (phase 7 review, D-063).
        "rage": rage.curtain(8, "green", "orange"),
        "stats": stats(
            record(
                {
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
                }
            )
        ),
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
    }
)
