"""P10-R11, 4-3: the Obsidian Golem, the final boss of the Lava fields level ().

Offsets in px from the boss's centre, X right and Y up (its chest faces down the screen, at -Y).
Its two huge fists hang on arms bending at the shoulder and the elbow (D-061), pumping in turn. The
stage patterns are the agent's design (P07-R04): the parts fire the same while they stand, the core
fires something new at every stage, and its last stage (only the core left) magma bombs and spirals
used by no earlier stage. Health tuned for P10-R12 with the D-055 bot.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import (
    bullet,
    bursting,
    mirror,
    part,
    stages,
    stats,
    twin,
    volley,
)
from game.config.bosses.boss_rage import rage
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


RED = bullet("red", 215)
ORANGE = bullet("orange", 205)
MAGENTA = bullet("magenta", 210)
PURPLE = bullet("purple", 200)
# The fists' magma: slow, big globs thrown out in rings (P10-R11).
MAGMA = bullet("orange", 110, 9)
# The last stage's magma bomb: a slow glob bursting into a ring of small drops.
BOMB = bursting("red", 120, 8, [1.1, 10, bullet("orange", 170)])

# The arms, by side.
ARMS = ["left", "right"]

# Where the left arm (at -X) bends and holds its fist, as drawn at rest: its shoulder, its elbow
# and its fist's centre. The right arm mirrors it.
GOLEM_ARM = record({"shoulder": [-40, -2], "elbow": [-60, -16], "fist": [-72, -42]})

# Where its other parts stand: the left shoulder cannon (mirrored), the plate, the emitter.
GOLEM_PARTS = record({"cannon": [-46, 20], "plate": [0, -34], "emitter": [0, -58]})

# How the arms pump (D-061): degrees at the shoulder and the elbow, seconds of one swing.
PUMP = record({"shoulderDeg": 9, "elbowDeg": 14, "period": 4.2, "lag": 0.25})


def side_of(arm: str) -> Any:
    """The side of `arm`: +1 for the left one (drawn at -X, as in `GOLEM_ARM`), -1 for the right."""
    return 1 if arm == "left" else -1


def arm_joints(arm: str) -> Any:
    """The shoulder and elbow joints of `arm`, the right one half a swing out of step."""
    s = side_of(arm)
    phase = 0 if arm == "left" else 0.5
    sx = GOLEM_ARM.shoulder[0]
    sy = GOLEM_ARM.shoulder[1]
    ex = GOLEM_ARM.elbow[0]
    ey = GOLEM_ARM.elbow[1]
    joints: dict[str, Any] = {}
    joints["shoulder-" + arm] = {
        "x": s * sx,
        "y": sy,
        "swing": {"amplitudeDeg": s * PUMP.shoulderDeg, "period": PUMP.period, "phase": phase},
    }
    joints["elbow-" + arm] = {
        "x": s * ex,
        "y": ey,
        "parent": "shoulder-" + arm,
        "swing": {
            "amplitudeDeg": s * PUMP.elbowDeg,
            "period": PUMP.period,
            "phase": phase + PUMP.lag,
        },
    }
    return joints


# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.

# The left fist's magma vent, in the middle of its knuckles (mirrored on the right).
GOLEM_KNUCKLES = [[-72, -57, 7]]
# The left shoulder cannon's twin barrels, as its turret rests (mirrored on the right).
GOLEM_CANNON_GUNS = twin(-46, 5, 15, 2.6)
# The chest emitter's lens, at the front of its prow (its laser fires straight down).
GOLEM_LENS = [[0, -68, 6]]
# The twin guns under its brow (the core's aimed shots, bursts, fans and bombs).
GOLEM_BROW = twin(6, -24, 22)
# The furnace stack on its back (the core's rings and spirals).
GOLEM_STACK = [[0, 30, 30]]

FIST_X = GOLEM_ARM.fist[0]
FIST_Y = GOLEM_ARM.fist[1]
CANNON_X = GOLEM_PARTS.cannon[0]
CANNON_Y = GOLEM_PARTS.cannon[1]


def fist(arm: str, health: float) -> Any:
    """`arm`'s fist, on its elbow (P10-R11): it shields the core."""
    return fpart(
        "fist-" + arm,
        [side_of(arm) * FIST_X, FIST_Y],
        17,
        health,
        {"joint": "elbow-" + arm},
    )


# 4-3: a massive armoured flying fortress of black obsidian plates with glowing magma seams and two
# huge fists (P10-R11). The fists throw rings of slow magma and, with the armour plate on its chest,
# shield the core; the shoulder cannons turn to fire aimed spreads; the chest emitter on its prow
# fires a laser straight down. The emitter hangs in front of the plate, so it can always be shot.
OBSIDIAN_GOLEM = record(
    {
        "id": "obsidian-golem",
        # Angry after each destroyed part (phase 7 review, D-063).
        "rage": concat(
            rage.flower(12, "orange", "red", 0.5), rage.vortex(12, "red", "magenta", 0.5)
        ),
        "stats": stats(
            record(
                {
                    "id": "obsidian-golem",
                    "name": "Obsidian Golem",
                    "size": 5.5,
                    "coreRadius": 24,
                    "coreHealth": 5200,
                    "points": 16000,
                    "groundSpeed": 0.3,
                    "coreDrop": 1,
                    "parts": [
                        fist("left", 1600),
                        fist("right", 1600),
                        fpart("cannon-left", [CANNON_X, CANNON_Y], 13, 1100, {"shields": False}),
                        fpart("cannon-right", [-CANNON_X, CANNON_Y], 13, 1100, {"shields": False}),
                        fpart("emitter", list(GOLEM_PARTS.emitter), 12, 800, {"shields": False}),
                        fpart("plate", list(GOLEM_PARTS.plate), 16, 1000),
                    ],
                    "joints": merge(arm_joints("left"), arm_joints("right")),
                }
            )
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 24, "period": 12},
        "bob": {"amplitude": 5, "period": 6},
        "guns": {
            "core": {"gun": GOLEM_BROW, "ring": GOLEM_STACK},
            "fist-left": {"gun": GOLEM_KNUCKLES},
            "fist-right": {"gun": mirror(GOLEM_KNUCKLES)},
            "cannon-left": {"gun": GOLEM_CANNON_GUNS, "turret": [CANNON_X, CANNON_Y]},
            "cannon-right": {"gun": mirror(GOLEM_CANNON_GUNS), "turret": [-CANNON_X, CANNON_Y]},
            "emitter": {"laser": GOLEM_LENS},
        },
        "stages": stages(
            [
                volley.ring("fist-left", 4.4, 8, 11, MAGMA, 1.6),
                volley.ring("fist-right", 4.4, 8, -11, MAGMA, 3.8),
                volley.aimed("cannon-left", 3, 3, 12, MAGENTA, 1),
                volley.aimed("cannon-right", 3, 3, 12, MAGENTA, 2.5),
                volley.laser("emitter", 7, 1.6, 4),
            ],
            [
                [volley.aimed("core", 2.6, 1, 0, RED, 1.4)],
                [volley.burst("core", 2.5, 4, 0.13, RED, 0.8)],
                [volley.fan("core", 2.5, 5, 14, ORANGE, 0.6)],
                [volley.ring("core", 1.6, 10, 8, PURPLE, 0.5)],
                [
                    volley.fan("core", 2.3, 7, 12, ORANGE, 0.6),
                    volley.burst("core", 2.9, 3, 0.13, RED, 1.3),
                ],
                [
                    volley.ring("core", 1.5, 12, -9, PURPLE, 0.5),
                    volley.aimed("core", 2.4, 3, 12, RED, 1.1),
                ],
                [
                    volley.aimed("core", 2.4, 1, 0, BOMB, 0.6),
                    volley.ring("core", 1.3, 12, 11, ORANGE, 0.4),
                    volley.ring("core", 1.3, 12, -13, PURPLE, 1.05),
                ],
            ],
        ),
    }
)
