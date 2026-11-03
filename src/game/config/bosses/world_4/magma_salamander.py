# Copyright (c) 2026 Renaud Guillon
"""4-3: the Magma Salamander (specs/bosses/mini/4-3-magma-salamander.md).

The mini boss of the Lava fields level. Offsets in px from the boss's centre, X right and Y up (its
snout points down, at -Y). Its tail curls back to its right and swings on two joints (D-061),
sweeping lines of bullets across the screen. The stage patterns are the agent's design
(MB-MAGMA-SALAMANDER-11): the fins and the tail fire the same while they stand, the core fires aimed
bursts that change at every stage, and its last stage (only the core left) a spiral used by no
earlier stage. Health (MB-MAGMA-SALAMANDER-08) tuned for WLD-4-22 with the D-055 bot.
"""

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.record import concat, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


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

# How the tail swings (D-061, MB-MAGMA-SALAMANDER-06): a slow lash at the root, the tip following
# a little later.
LASH = record({"rootDeg": 12, "tipDeg": 18, "period": 3.6, "lag": 0.2})

ROOT_X = SALAMANDER_TAIL.root[0]
ROOT_Y = SALAMANDER_TAIL.root[1]
KNUCKLE_X = SALAMANDER_TAIL.knuckle[0]
KNUCKLE_Y = SALAMANDER_TAIL.knuckle[1]

# The tail's two joints: its root, and its tip's knuckle hanging on it.
TAIL_JOINTS = record({
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
})

# Headings of one sweep of the tail's line, left to right across the screen (degrees).
SWEEP = [-45, -35, -25, -15, -5, 5, 15, 25, 35, 45]
# Seconds between two drops of a sweep, and between two sweeps (there, then back).
SWEEP_GAP = 0.12
SWEEP_EVERY = 5.2


def sweep(first: float) -> Any:
    """Return the tail's sweeping lines (MB-MAGMA-SALAMANDER-10).

    Single drops at preset headings fired one after the other, left to right then back, so a line of
    bullets swings across the screen.
    """
    count = len(SWEEP)
    headings = concat(SWEEP, [SWEEP[count - 1 - i] for i in range(count)])
    return [
        volley.fan("tail", SWEEP_EVERY, 1, 0, DROP, first + SWEEP_GAP * i, heading)
        for i, heading in enumerate(headings)
    ]


FIN_X = SALAMANDER_PARTS.fin[0]
FIN_Y = SALAMANDER_PARTS.fin[1]

# 4-3: a segmented lizard-ship with a molten glow between its plates, orange-yellow neon
# (MB-MAGMA-SALAMANDER-01). Its two back fins fire fans and shield the core; its tail, curled back
# to its right so it can be shot past the core, lashes on its joints and sweeps lines of bullets;
# the core fires aimed bursts from its jaws.
_MAGMA_SALAMANDER = record({
    "id": "magma-salamander",
    # Angry after each destroyed part (phase 7 review, D-063, MB-MAGMA-SALAMANDER-12).
    "rage": rage.curtain(11, "orange", "red"),
    # Its core and parts, their health, and its points (MB-MAGMA-SALAMANDER-08,
    # MB-MAGMA-SALAMANDER-16).
    "stats": stats(
        record({
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
        })
    ),
    # Where it stops and how it moves in place (MB-MAGMA-SALAMANDER-07).
    "stopFraction": 0.74,
    "sway": {"amplitude": 56, "period": 7},
    "bob": {"amplitude": 8, "period": 3.4},
    "guns": {
        "core": {"gun": SALAMANDER_JAWS, "ring": SALAMANDER_VENT},
        "fin-left": {"gun": SALAMANDER_FIN_GUNS},
        "fin-right": {"gun": mirror(SALAMANDER_FIN_GUNS)},
        "tail": {"gun": SALAMANDER_STINGER},
    },
    # In every stage the fins' fans (MB-MAGMA-SALAMANDER-09) and the tail's lines; then the
    # core's bursts per stage (MB-MAGMA-SALAMANDER-11).
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
})

# Its hidden weapons (boss transformations, D-224, MB-MAGMA-SALAMANDER-13): at transformation 1 its
# back plating bursts off, baring a dark metal frame, and a pair of sweeping lasers unfold
# (MB-MAGMA-SALAMANDER-14).
MAGMA_SALAMANDER = with_weapons(
    _MAGMA_SALAMANDER,
    [
        hidden_weapon("sweeper-left", "sweeper", [-9, 13], 7, 720, 1, "orange", 1.2, 12.4),
        hidden_weapon("sweeper-right", "sweeper", [9, 13], 7, 720, 1, "orange", 2.0, 12.4),
    ],
    [
        # MB-MAGMA-SALAMANDER-13: the back plating, the three scale plates over its back as shells
        # on the flattened belly (their footprint; the nose at -Y, see
        # `magma_salamander_armour.PLATES`); the sweepers lie under it.
        armour_region(
            "back",
            1,
            [
                [-7, 26],
                [7, 26],
                [8, 18],
                [13.5, 17],
                [13.5, 4],
                [14.5, 2],
                [14.5, -10],
                [-14.5, -10],
                [-14.5, 2],
                [-13.5, 4],
                [-13.5, 17],
                [-8, 18],
            ],
            "shell",
            None,
            False,
        ),
    ],
)
