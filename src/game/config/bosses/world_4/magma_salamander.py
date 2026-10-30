"""P10-R11, 4-3: the Magma Salamander, the mini boss of the Lava fields level ().

Offsets in px from the boss's centre, X right and Y up (its snout points down, at -Y). Its tail
curls back to its right and swings on two joints (D-061), sweeping lines of bullets across the
screen. The stage patterns are the agent's design (P07-R04): the fins and the tail fire the same
while they stand, the core fires aimed bursts that change at every stage, and its last stage (only
the core left) a spiral used by no earlier stage. Health tuned for P10-R12 with the D-055 bot.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import concat, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

RED = bullet("red", 215)
ORANGE = bullet("orange", 210)
MAGENTA = bullet("magenta", 205)
# The tail's sweeping lines: small, quick drops of magma.
DROP = bullet("orange", 230, 3.5)

# Where its parts stand (the left fin, at -X; the right one mirrors it), and its tail's tip.
SALAMANDER_PARTS = record({"fin": [-34, 4], "tail": [19, 50]})

# The tail's joints (D-061): its root on the body, and the knuckle where its tip bends.
SALAMANDER_TAIL = record({"root": [0, 24], "knuckle": [12, 42]})

# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.

# The left fin's twin fan barrels, under its leading edge (mirrored on the right).
SALAMANDER_FIN_GUNS = twin(-34, -10, 4, 2.4)
# The stinger at the tail's tip: the sweeping lines leave from it.
SALAMANDER_STINGER = [[21, 57, 8]]
# The twin guns in its jaws (the core's aimed bursts).
SALAMANDER_JAWS = twin(5, -64, 2)
# The magma vent on its back, between the fins (the core's last-stage spiral).
SALAMANDER_VENT = [[0, 10, 15]]

# How the tail swings (D-061): a slow lash at the root, the tip following a little later.
LASH = record({"rootDeg": 12, "tipDeg": 18, "period": 3.6, "lag": 0.2})

ROOT_X = SALAMANDER_TAIL.root[0]
ROOT_Y = SALAMANDER_TAIL.root[1]
KNUCKLE_X = SALAMANDER_TAIL.knuckle[0]
KNUCKLE_Y = SALAMANDER_TAIL.knuckle[1]

# The tail's two joints: its root, and its tip's knuckle hanging on it.
TAIL_JOINTS = record(
    {
        "tail-root": {
            "x": ROOT_X,
            "y": ROOT_Y,
            "swing": {"amplitudeDeg": LASH.rootDeg, "period": LASH.period},
        },
        "tail-tip": {
            "x": KNUCKLE_X,
            "y": KNUCKLE_Y,
            "parent": "tail-root",
            "swing": {"amplitudeDeg": LASH.tipDeg, "period": LASH.period, "phase": LASH.lag},
        },
    }
)

# Headings of one sweep of the tail's line, left to right across the screen (degrees).
SWEEP = [-45, -35, -25, -15, -5, 5, 15, 25, 35, 45]
# Seconds between two drops of a sweep, and between two sweeps (there, then back).
SWEEP_GAP = 0.12
SWEEP_EVERY = 5.2


def sweep(first: float) -> Any:
    """The tail's sweeping lines (P10-R11): single drops at preset headings fired one after the
    other, left to right then back, so a line of bullets swings across the screen.
    """
    count = len(SWEEP)
    headings = concat(SWEEP, [SWEEP[count - 1 - i] for i in range(count)])
    return [
        volley.fan("tail", SWEEP_EVERY, 1, 0, DROP, first + SWEEP_GAP * i, heading)
        for i, heading in enumerate(headings)
    ]


FIN_X = SALAMANDER_PARTS.fin[0]
FIN_Y = SALAMANDER_PARTS.fin[1]

# 4-3: a segmented lizard-ship with a molten glow between its plates, orange-yellow neon (P10-R11).
# Its two back fins fire fans and shield the core; its tail, curled back to its right so it can be
# shot past the core, lashes on its joints and sweeps lines of bullets; the core fires aimed bursts
# from its jaws.
MAGMA_SALAMANDER = record(
    {
        "id": "magma-salamander",
        # Angry after each destroyed part (phase 7 review, D-063).
        "rage": rage.curtain(11, "orange", "red"),
        "stats": stats(
            record(
                {
                    "id": "magma-salamander",
                    "name": "Magma Salamander",
                    "size": 3.5,
                    "coreRadius": 16,
                    "coreHealth": 2000,
                    "points": 8000,
                    "groundSpeed": 0.6,
                    "parts": [
                        part("fin-left", [FIN_X, FIN_Y], 13, 900),
                        part("fin-right", [-FIN_X, FIN_Y], 13, 900),
                        part(
                            "tail",
                            list(SALAMANDER_PARTS.tail),
                            12,
                            700,
                            {"shields": False, "joint": "tail-tip"},
                        ),
                    ],
                    "joints": TAIL_JOINTS,
                }
            )
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 56, "period": 7},
        "bob": {"amplitude": 8, "period": 3.4},
        "guns": {
            "core": {"gun": SALAMANDER_JAWS, "ring": SALAMANDER_VENT},
            "fin-left": {"gun": SALAMANDER_FIN_GUNS},
            "fin-right": {"gun": mirror(SALAMANDER_FIN_GUNS)},
            "tail": {"gun": SALAMANDER_STINGER},
        },
        "stages": stages(
            concat(
                [
                    # The fins' fans cross under its snout, each leaning towards the other side.
                    volley.fan("fin-left", 2.6, 3, 13, MAGENTA, 1.1, 9),
                    volley.fan("fin-right", 2.6, 3, 13, MAGENTA, 2.4, -9),
                ],
                sweep(2),
            ),
            [
                [volley.burst("core", 2.5, 3, 0.13, RED, 1.4)],
                [volley.burst("core", 2.3, 4, 0.12, RED, 0.8)],
                [
                    volley.burst("core", 1.5, 3, 0.11, ORANGE, 0.6),
                    volley.burst("core", 3, 5, 0.1, RED, 1.3),
                ],
                [
                    volley.ring("core", 0.42, 6, 19, ORANGE, 0.3),
                    volley.burst("core", 2.2, 4, 0.11, RED, 1),
                ],
            ],
        ),
    }
)
