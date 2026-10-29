"""The Harbour Kraken (P08-R10, 2-2's final boss), ported from
`config/bosses/world-2/harbour-kraken.ts`.

Its four crane arms swing at the shoulder and the elbow (D-061), each out of step with the others.
Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

RED = bullet("red", 190)
MAGENTA = bullet("magenta", 185)
ORANGE = bullet("orange", 175)


def fpart(part_id: str, at: list[Any], radius: float, health: float, options: Any = None) -> Any:
    """A final boss's part: drops a bonus 60 % of the time (P07-R07, `part_drop_chance`)."""
    extra = {} if options == None else options  # noqa: E711
    return part(part_id, at, radius, health, merge({"drop": 0.6}, extra))


# The cranes, by id: `fore` at the bow, `aft` at the stern, either side (`Crane` in the TS):
# "fore-left", "fore-right", "aft-left", "aft-right".

# Where a left crane (at -X) turns and holds its grab cannon, as drawn at rest: its shoulder (on
# its pedestal), its elbow and its grab's centre. The right ones mirror them.
CRANE_REST = {
    "fore": [
        [-28, -26],
        [-50, -34],
        [-70, -44],
    ],
    "aft": [
        [-28, 22],
        [-52, 27],
        [-72, 34],
    ],
}

# How each crane swings (phase 7 review, D-061): degrees and seconds at the shoulder and the
# elbow, and its phase, so that the four arms never move together.
SWING = {
    "fore-left": [10, 18, 0],
    "fore-right": [10, 18, 0.31],
    "aft-left": [9, 16, 0.58],
    "aft-right": [9, 16, 0.83],
}


def crane_joints(crane: str) -> Any:
    """The shoulder and elbow joints of `crane`."""
    end, side = crane.split("-")
    s = 1 if side == "left" else -1
    rest: Any = CRANE_REST[end]
    shoulder = rest[0]
    elbow = rest[1]
    swing: Any = SWING[crane]
    a = swing[0]
    b = swing[1]
    phase = swing[2]
    table: Any = {}
    table["shoulder-" + crane] = record(
        {
            "x": s * shoulder[0],
            "y": shoulder[1],
            "swing": {"amplitudeDeg": s * a, "period": 5.2, "phase": phase},
        }
    )
    table["elbow-" + crane] = record(
        {
            "x": s * elbow[0],
            "y": elbow[1],
            "parent": "shoulder-" + crane,
            "swing": {"amplitudeDeg": -s * b, "period": 3.7, "phase": phase + 0.2},
        }
    )
    return table


# The cranes in the order of their parts.
CRANES = ["fore-left", "fore-right", "aft-left", "aft-right"]


def crane_joint_table() -> Any:
    """The joints of all four cranes, by name."""
    table: Any = {}
    for crane in CRANES:
        table = merge(table, crane_joints(crane))
    return table


def grab(crane: str, health: float) -> Any:
    """A crane's grab cannon, on its elbow (the part's centre is its grab's)."""
    end, side = crane.split("-")
    x = CRANE_REST[end][2][0]
    y = CRANE_REST[end][2][1]
    return fpart(
        "crane-" + crane,
        [x if side == "left" else -x, y],
        13,
        health,
        {"joint": "elbow-" + crane},
    )


# The guns' muzzles (phase 7 review): the tips of the barrels its model draws, from the boss's
# centre, X right, Y up, and height above the playfield (see `BossDesign.guns`), at rest.

# The grab cannons' barrels: the left fore one and the left aft one (mirrored on the right).
GRAB_FORE = [-70, -59.82, 4]
GRAB_AFT = [-72, 18.18, 4]
# The bow's laser emitter, and the twin guns either side of it.
BOW_LASER = [0, -78.4, 6]
BOW_GUNS = twin(9, -67.68, 9.5)


def sided(m: list[Any], side: float) -> list[list[Any]]:
    """The left crane's muzzle `m`, on `side` (1 for the left, -1 for the right)."""
    return [[side * m[0], m[1], m[2]]]


# 2-2: a cargo crane-ship with four crane arms swinging at the shoulder and the elbow, orange neon
# (P08-R10). The four grab cannons shield the core; the container bay at the stern launches
# Gnats. The ground stops: the fight is over the harbour.
HARBOUR_KRAKEN = record(
    {
        "id": "harbour-kraken",
        # Angry after each destroyed part (phase 7 review).
        "rage": rage.vortex(4, "orange", "magenta"),
        "stats": stats(
            {
                "id": "harbour-kraken",
                "name": "Harbour Kraken",
                "size": 5,
                "coreRadius": 22,
                "coreHealth": 2700,
                "points": 10500,
                "groundSpeed": 0,
                "coreDrop": 1,
                "parts": concat(
                    [grab(crane, 900) for crane in CRANES],
                    [fpart("container-bay", [0, 46], 16, 700, {"shields": False})],
                ),
                "joints": crane_joint_table(),
            }
        ),
        "stopFraction": 0.75,
        "sway": {"amplitude": 35, "period": 10},
        "bob": {"amplitude": 6, "period": 5},
        "launches": [
            {"from": "container-bay", "kind": "gnats", "count": 3, "every": 7, "first": 3}
        ],
        "guns": {
            "core": {"gun": BOW_GUNS, "laser": [BOW_LASER]},
            "crane-fore-left": {"gun": sided(GRAB_FORE, 1)},
            "crane-fore-right": {"gun": sided(GRAB_FORE, -1)},
            "crane-aft-left": {"gun": sided(GRAB_AFT, 1)},
            "crane-aft-right": {"gun": sided(GRAB_AFT, -1)},
        },
        "stages": stages(
            [
                volley.burst("crane-fore-left", 3, 3, 0.16, RED, 1),
                volley.burst("crane-fore-right", 3, 3, 0.16, RED, 1.75),
                volley.burst("crane-aft-left", 3, 3, 0.16, RED, 2.5),
                volley.burst("crane-aft-right", 3, 3, 0.16, RED, 3.25),
            ],
            [
                [volley.laser("core", 7, 1.5, 4)],
                [volley.laser("core", 6, 1.5, 2), volley.aimed("core", 2.6, 1, 0, MAGENTA, 1)],
                [volley.laser("core", 5.5, 1.5, 2), volley.fan("core", 2.6, 5, 14, MAGENTA, 1)],
                [volley.laser("core", 5.5, 1.6, 2), volley.aimed("core", 2.4, 3, 12, MAGENTA, 0.8)],
                [volley.laser("core", 5, 1.6, 2), volley.fan("core", 2.2, 7, 12, MAGENTA, 0.6)],
                [volley.laser("core", 4.5, 1.6, 1.5), volley.ring("core", 1.4, 14, 9, ORANGE, 0.4)],
            ],
        ),
    }
)
