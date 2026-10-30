"""P09-R09, 3-1: the River Leviathan, the River delta's final boss ().

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Its head is
the core, at the centre; its body trails behind it (+Y) in four segments and a tail, each hinged on
the one before (D-061, chained joints). Every hinge swings the same way a little later than the one
before, so a wave runs down the body from the head to the tail, as a swimming snake's.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, cells, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

TEAL = bullet("green", 195)
BLUE = bullet("blue", 205)
MAGENTA = bullet("magenta", 200)
PURPLE = bullet("purple", 210)


def fpart(part_id: str, at: Any, radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
    return part(part_id, at, radius, health, merge({"drop": 0.6}, options))


# The body's segments, head to tail.
SEGMENTS = [1, 2, 3, 4]

# The body (rest pose, straight behind the head): the hinge of each segment (`neck` for the first)
# and of the tail, along the spine; each segment's middle; the side of its turret's sponson (they
# alternate, so that none hides right behind the head) and how far out it is.
LEVIATHAN_BODY = record(
    {
        "hinges": [20, 52, 84, 116, 148],
        "middles": [36, 68, 100, 132],
        "sides": [-1, 1, -1, 1],
        "turretOut": 28,
        # The missile rack's middle, on the tail.
        "rack": 166,
    }
)

# How each hinge swings (D-061): degrees either way, growing towards the tail, all over one
# `period`, each `lag` of a period behind the one before (the wave running down the body).
SWAY = record({"degrees": [8, 9, 10, 12, 14], "period": 4.8, "lag": 0.11})

# The joint ids, head to tail: the neck, three spine hinges, the tail's.
LEVIATHAN_JOINTS = ["neck", "spine-1", "spine-2", "spine-3", "tail"]


def spine() -> Any:
    """The chain of joints, each hanging on the one before it."""
    joints: dict[str, Any] = {}
    for i, joint_id in enumerate(LEVIATHAN_JOINTS):
        entry: dict[str, Any] = {
            "x": 0,
            "y": LEVIATHAN_BODY.hinges[i],
            "swing": {
                "amplitudeDeg": SWAY.degrees[i],
                "period": SWAY.period,
                "phase": 1 - SWAY.lag * i,
            },
        }
        if i > 0:
            entry["parent"] = LEVIATHAN_JOINTS[i - 1]
        joints[joint_id] = entry
    return joints


def turret_at(k: int) -> Any:
    """Where segment `k`'s turret sits, at rest: on its sponson, out to one side."""
    i = k - 1
    return [LEVIATHAN_BODY.sides[i] * LEVIATHAN_BODY.turretOut, LEVIATHAN_BODY.middles[i]]


# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The ring emitter on top of each segment turret, on its axis: it stays put as the turret turns
# with its rings (D-060), and its rings fire from it (its `gun`, as rings fall back on it).
TURRET_EMITTER_HEIGHT = 15.5


def turret_emitter(k: int) -> Any:
    """The ring emitter of segment `k`'s turret."""
    return [concat(turret_at(k), [TURRET_EMITTER_HEIGHT])]


# The head's laser lens, at the tip of its snout.
LEVIATHAN_LENS = [[0, -31, 5]]
# The head's twin fang guns either side of its jaw (the core's aimed shots and fans).
LEVIATHAN_FANGS = twin(9, -24, 3.5)
# The crest emitter on the top of its head (the core's last-stage spirals).
LEVIATHAN_CREST = [[0, 2, 19]]
# The missile rack's cells on the tail, two by two.
LEVIATHAN_RACK = cells([-4.5, 4.5], [160, 170], 10)


def segment_guns() -> Any:
    """The guns of the four segment turrets, keyed by part id."""
    guns: dict[str, Any] = {}
    for k in SEGMENTS:
        guns["segment-" + str(k)] = {"gun": turret_emitter(k), "turret": turret_at(k)}
    return guns


# 3-1: a segmented serpent-ship 6 L long, its body swaying from side to side, teal neon along its
# spine (P09-R09). Its four segments' turrets fire rings in turn and shield the core; the tail's
# rack fires homing missiles; the head fires its laser at every stage, with something new beside
# it. The ground slows (x0.5).
RIVER_LEVIATHAN = record(
    {
        "id": "river-leviathan",
        # Angry after each destroyed part (D-063), heat 5 (P09-R10).
        "rage": rage.spirals(5, "blue", "green"),
        "stats": stats(
            record(
                {
                    "id": "river-leviathan",
                    "name": "River Leviathan",
                    "size": 6,
                    "coreRadius": 22,
                    "coreHealth": 2500,
                    "points": 20000,
                    "groundSpeed": 0.5,
                    "coreDrop": 1,
                    "parts": concat(
                        [
                            fpart(
                                "segment-" + str(k),
                                turret_at(k),
                                14,
                                900,
                                {"joint": LEVIATHAN_JOINTS[k - 1]},
                            )
                            for k in SEGMENTS
                        ],
                        [
                            fpart(
                                "tail-rack",
                                [0, LEVIATHAN_BODY.rack],
                                13,
                                700,
                                {"shields": False, "joint": "tail"},
                            )
                        ],
                    ),
                    "joints": spine(),
                }
            )
        ),
        # Stops high enough to be in place within 6.5 s (P07-R05), its tail still on screen.
        "stopFraction": 0.72,
        "sway": {"amplitude": 55, "period": 9.6},
        "bob": {"amplitude": 6, "period": 4.8},
        "guns": merge(
            merge(
                {
                    "core": {
                        "gun": LEVIATHAN_FANGS,
                        "laser": LEVIATHAN_LENS,
                        "ring": LEVIATHAN_CREST,
                    }
                },
                segment_guns(),
            ),
            {"tail-rack": {"missile": LEVIATHAN_RACK}},
        ),
        "stages": stages(
            concat(
                # The segments' rings in turn, from the neck to the tail, one a second.
                [volley.ring("segment-" + str(k), 4.4, 8, 11, TEAL, 1.1 * k) for k in SEGMENTS],
                [volley.missiles("tail-rack", 6, 2, 30, 3)],
            ),
            [
                [volley.laser("core", 7, 1.5, 4)],
                [
                    volley.laser("core", 6.5, 1.5, 2),
                    volley.aimed("core", 2.8, 3, 12, MAGENTA, 1),
                ],
                [
                    volley.laser("core", 6, 1.5, 2),
                    volley.fan("core", 2.6, 5, 14, MAGENTA, 0.8),
                ],
                [
                    volley.laser("core", 6, 1.6, 2),
                    volley.burst("core", 2.6, 4, 0.14, BLUE, 0.6),
                ],
                [
                    volley.laser("core", 5.5, 1.6, 2),
                    volley.fan("core", 2.4, 7, 12, MAGENTA, 0.6),
                ],
                # Alone: two spirals turning opposite ways from its crest, under the laser.
                [
                    volley.laser("core", 5, 1.6, 1.5),
                    volley.ring("core", 0.5, 4, 19, BLUE, 0.4),
                    volley.ring("core", 0.5, 4, -23, PURPLE, 0.65),
                ],
            ],
        ),
    }
)
